#!/usr/bin/env python3
"""
icingadb-top-notifications.py — Alarm-Fatigue-Analyse für IcingaDB

Fragt die IcingaDB-Datenbank nach häufigen Notifications ab und gibt
die Ergebnisse tabellarisch, als CSV oder JSON aus.

Beispiele:
  # Top-Lärmer letzte 7 Tage, ohne Recoveries
  ./icingadb-top-notifications.py --no-recoveries

  # Nur ein Host, letzter Monat
  ./icingadb-top-notifications.py --days 30 --host thrud

  # CSV für weitere Verarbeitung
  ./icingadb-top-notifications.py --format csv --only-problems | sort -t, -k3 -rn

  # Bestimmtes Zeitfenster
  ./icingadb-top-notifications.py --since 2026-03-01 --until 2026-03-26 --limit 50

Hinweis: chmod +x icingadb-top-notifications.py
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone


def parse_args():
    parser = argparse.ArgumentParser(
        description="IcingaDB Top-Notifications — Alarm Fatigue Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Zeitfenster
    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument(
        "--days", type=int, default=7,
        help="Time window in days, counting back from now (default: 7)"
    )
    time_group.add_argument(
        "--since", metavar="YYYY-MM-DD",
        help="Start date ISO (overrides --days)"
    )
    parser.add_argument(
        "--until", metavar="YYYY-MM-DD",
        help="End date ISO, inclusive until 23:59:59 UTC (default: now)"
    )

    # Filter
    parser.add_argument("--limit", type=int, default=30, help="Number of results (default: 30)")
    parser.add_argument("--host", metavar="PATTERN", help="Filter by host name (LIKE match, e.g. 'thrud%%')")
    parser.add_argument("--service", metavar="PATTERN", help="Filter by service name (LIKE match)")
    parser.add_argument(
        "--no-recoveries", action="store_true",
        help="Exclude notifications of type 'recovery'"
    )
    parser.add_argument(
        "--only-problems", action="store_true",
        help="Only include type='notification' (hard alerts only)"
    )

    # DB-Verbindung
    parser.add_argument("--db-host", default="localhost", help="MySQL host (default: localhost)")
    parser.add_argument("--db-port", type=int, default=3306, help="MySQL port (default: 3306)")
    parser.add_argument("--db-name", default="icingadb", help="Database name (default: icingadb)")
    parser.add_argument("--db-user", default="icingadb", help="Database user (default: icingadb)")
    parser.add_argument(
        "--db-password", metavar="PASSWORD",
        help="Database password (prefer env var ICINGADB_PASSWORD)"
    )

    parser.add_argument(
        "--format", choices=["table", "csv", "json"], default="table",
        help="Output format (default: table)"
    )

    return parser.parse_args()


def get_password(args):
    """Passwort aus Env-Var oder CLI-Argument — nie in der Prozessliste sichtbar."""
    return os.environ.get("ICINGADB_PASSWORD") or args.db_password or ""


def resolve_time_range(args):
    """Gibt (ts_start, ts_end) als Unix-Timestamps in Sekunden zurück."""
    now = datetime.now(tz=timezone.utc)

    if args.until:
        try:
            ts_end = int(datetime.strptime(args.until, "%Y-%m-%d")
                        .replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                        .timestamp())
        except ValueError:
            sys.exit(f"Error: invalid --until date '{args.until}'. Expected format: YYYY-MM-DD")
    else:
        ts_end = int(now.timestamp())

    if args.since:
        try:
            ts_start = int(datetime.strptime(args.since, "%Y-%m-%d")
                          .replace(tzinfo=timezone.utc)
                          .timestamp())
        except ValueError:
            sys.exit(f"Error: invalid --since date '{args.since}'. Expected format: YYYY-MM-DD")
    else:
        ts_start = int((now - timedelta(days=args.days)).timestamp())

    return ts_start, ts_end


def detect_send_time_unit(cursor):
    """
    Detects whether send_time is stored in seconds, milliseconds, or microseconds
    and returns the SQL expression that normalises it to seconds.

    Thresholds (valid for timestamps from year 2001 onwards):
      > 10^14  →  microseconds  (÷ 1_000_000)
      > 10^11  →  milliseconds  (÷ 1_000)
      else     →  seconds       (no division)

    Year-2024 values:  ~1.7e9 s  /  ~1.7e12 ms  /  ~1.7e15 µs
    """
    cursor.execute(
        "SELECT send_time FROM notification_history ORDER BY send_time DESC LIMIT 1"
    )
    row = cursor.fetchone()
    if not row:
        return "send_time"
    # pymysql uses DictCursor, mysql.connector returns plain tuples
    val = row["send_time"] if isinstance(row, dict) else row[0]
    if not val:
        return "send_time"
    if val > 100_000_000_000_000:   # > 10^14 → microseconds
        return "send_time / 1000000"
    if val > 100_000_000_000:       # > 10^11 → milliseconds
        return "send_time / 1000"
    return "send_time"


def build_query(send_time_expr, ts_start, ts_end, args):
    conditions = [
        f"{send_time_expr} >= %(ts_start)s",
        f"{send_time_expr} <= %(ts_end)s",
    ]
    params = {"ts_start": ts_start, "ts_end": ts_end, "limit": args.limit}

    if args.only_problems:
        conditions.append("nh.type = 'notification'")
    elif args.no_recoveries:
        conditions.append("nh.type != 'recovery'")

    if args.host:
        conditions.append("h.display_name LIKE %(host_pattern)s")
        params["host_pattern"] = args.host if "%" in args.host else f"%{args.host}%"

    if args.service:
        conditions.append("COALESCE(s.display_name, '') LIKE %(service_pattern)s")
        params["service_pattern"] = args.service if "%" in args.service else f"%{args.service}%"

    where = " AND ".join(conditions)

    # {where} enthält ausschließlich interne, fest codierte Condition-Strings.
    # Alle User-Eingaben fließen als parametrisierte Query-Parameter ein, nie per String-Interpolation.
    sql = f"""
        SELECT
            h.display_name                          AS host,
            COALESCE(s.display_name, '(host check)') AS service,
            COUNT(*)                                AS notifications
        FROM notification_history nh
        JOIN host h ON h.id = nh.host_id
        LEFT JOIN service s ON s.id = nh.service_id
        WHERE {where}
        GROUP BY h.display_name, s.display_name
        ORDER BY notifications DESC
        LIMIT %(limit)s
    """
    return sql, params


def connect_db(args, password):
    """Versucht pymysql, fällt auf mysql-connector-python zurück."""
    pymysql_available = False
    connector_available = False

    try:
        import pymysql
        pymysql_available = True
        conn = pymysql.connect(
            host=args.db_host,
            port=args.db_port,
            database=args.db_name,
            user=args.db_user,
            password=password,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
        )
        return conn, "pymysql"
    except ImportError:
        pass
    except Exception as e:
        _die_connection_error(args, e)

    try:
        import mysql.connector
        connector_available = True
        conn = mysql.connector.connect(
            host=args.db_host,
            port=args.db_port,
            database=args.db_name,
            user=args.db_user,
            password=password,
            connection_timeout=10,
        )
        return conn, "mysql.connector"
    except ImportError:
        pass
    except Exception as e:
        _die_connection_error(args, e)

    if not pymysql_available and not connector_available:
        sys.exit(
            "Error: no MySQL driver found.\n"
            "  pip install pymysql\n"
            "  or: pip install mysql-connector-python"
        )


def _die_connection_error(args, exc):
    password_hint = (
        "ICINGADB_PASSWORD env var (set)"
        if os.environ.get("ICINGADB_PASSWORD")
        else "--db-password (not provided)"
        if not args.db_password
        else "--db-password (provided)"
    )
    sys.exit(
        f"Error: database connection failed.\n"
        f"  Host:     {args.db_host}:{args.db_port}\n"
        f"  Database: {args.db_name}\n"
        f"  User:     {args.db_user}\n"
        f"  Password: {password_hint}\n"
        f"  Reason:   {exc}\n"
        f"\n"
        f"Adjust credentials with --db-host, --db-user, --db-password\n"
        f"or set the password via environment variable: export ICINGADB_PASSWORD=...\n"
        f"Help: {sys.argv[0]} --help"
    )


def fetchall_as_dicts(conn, driver, cursor, sql, params):
    """Einheitliche Dict-Ergebnisse für beide Treiber."""
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    if driver == "mysql.connector":
        cols = [d[0] for d in cursor.description]
        rows = [dict(zip(cols, row)) for row in rows]
    return rows


def output_table(rows, total):
    if not rows:
        print("No results.")
        return

    # tabulate verwenden falls vorhanden, sonst manuell
    try:
        from tabulate import tabulate
        table_rows = [
            (i + 1, r["host"], r["service"], r["notifications"],
             f"{r['notifications'] / total * 100:.1f}%" if total else "-")
            for i, r in enumerate(rows)
        ]
        print(tabulate(table_rows, headers=["#", "Host", "Service", "Count", "%"],
                       tablefmt="simple"))
    except ImportError:
        col_rank = 4
        col_host = max(len(r["host"]) for r in rows)
        col_host = max(col_host, 4)
        col_svc = max(len(r["service"]) for r in rows)
        col_svc = max(col_svc, 7)
        col_count = max(len(str(r["notifications"])) for r in rows)
        col_count = max(col_count, 5)

        header = (f"{'#':>{col_rank}}  {'Host':<{col_host}}  {'Service':<{col_svc}}"
                  f"  {'Count':>{col_count}}  {'%':>6}")
        sep = "-" * len(header)
        print(header)
        print(sep)
        for i, r in enumerate(rows):
            pct = f"{r['notifications'] / total * 100:.1f}%" if total else "-"
            print(f"{i+1:>{col_rank}}  {r['host']:<{col_host}}  {r['service']:<{col_svc}}"
                  f"  {r['notifications']:>{col_count}}  {pct:>6}")

    print()
    print(f"Total: {total} notifications in time window")


def output_csv(rows):
    writer = csv.writer(sys.stdout)
    writer.writerow(["rank", "host", "service", "count"])
    for i, r in enumerate(rows):
        writer.writerow([i + 1, r["host"], r["service"], r["notifications"]])


def output_json(rows):
    result = [
        {"rank": i + 1, "host": r["host"], "service": r["service"],
         "count": r["notifications"]}
        for i, r in enumerate(rows)
    ]
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    args = parse_args()
    password = get_password(args)
    ts_start, ts_end = resolve_time_range(args)

    conn, driver = connect_db(args, password)

    try:
        if driver == "pymysql":
            cursor = conn.cursor()
        else:
            cursor = conn.cursor()

        try:
            send_time_expr = detect_send_time_unit(cursor)
        except Exception as e:
            sys.exit(
                f"Error accessing notification_history: {e}\n"
                "Hint: 'DESCRIBE notification_history;' shows the table structure."
            )

        sql, params = build_query(send_time_expr, ts_start, ts_end, args)

        try:
            rows = fetchall_as_dicts(conn, driver, cursor, sql, params)
        except Exception as e:
            sys.exit(
                f"Error executing query: {e}\n"
                "Hint: 'DESCRIBE notification_history;' shows the table structure."
            )

        # Gesamtanzahl für %-Berechnung
        total = sum(r["notifications"] for r in rows)

        if args.format == "table":
            output_table(rows, total)
        elif args.format == "csv":
            output_csv(rows)
        elif args.format == "json":
            output_json(rows)

    except Exception as e:
        sys.exit(f"Datenbankfehler: {e}")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


if __name__ == "__main__":
    main()
