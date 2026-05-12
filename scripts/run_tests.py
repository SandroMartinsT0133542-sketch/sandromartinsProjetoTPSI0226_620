#!/usr/bin/env python3
"""Lightweight test harness for the fitness app.

Run with:

    PYTHONPATH=src python scripts/run_tests.py

This script is non-interactive and performs: user creation, authentication,
record creation, searches, sorts, statistics, filtering and saves state.
"""
from pprint import pprint
from datetime import datetime
import sys

from src.services.auth_service import initialize_auth, register_user, authenticate, current_user
from src.services.progress_service import (
    initialize_service, create_record, list_records, search_records,
    sort_records, compute_statistics, filter_weight_range, save_state
)

sys.path.insert(0, 'src')



def main() -> int:
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    username = f'test_runner_{timestamp}'
    display = 'Test Runner'
    password = 'Runner@123'

    print('Initializing auth...')
    initialize_auth()

    print(f'Registering user {username}...')
    ok, msg = register_user(username, display, password)
    print('Register:', ok, msg)
    if not ok:
        print('Registration failed; aborting.')
        return 2

    print('Authenticating...')
    if not authenticate(username, password):
        print('Authentication failed; aborting.')
        return 3
    print('Current user:', current_user())

    print('Initializing service...')
    initialize_service()

    print('Creating sample records...')
    create_record({
        'client_name':'Alice','email':'alice@example.com','phone':'123','record_date':'2026-05-01',
        'weight_kg':70.5,'body_fat_pct':18.2,'daily_calories':2200,'password':'', 'notes':'First'
    })
    create_record({
        'client_name':'Bob','email':'bob@example.com','phone':'456','record_date':'2026-05-02',
        'weight_kg':82.0,'body_fat_pct':22.1,'daily_calories':2500,'password':'', 'notes':'Second'
    })
    create_record({
        'client_name':'Carol','email':'carol@example.com','phone':'789','record_date':'2026-05-03',
        'weight_kg':64.2,'body_fat_pct':16.5,'daily_calories':2000,'password':'', 'notes':'Third'
    })

    recs = list_records()
    print('Records for current user:', len(recs))

    print('\nSearch by client_name=="Bob" (linear):')
    pprint(search_records('client_name','Bob','linear'))

    print('\nSearch by weight==64.2 (binary):')
    pprint(search_records('weight_kg',64.2,'binary'))

    print('\nSort by weight ascending (insertion):')
    print([r['client_name'] for r in sort_records('weight_kg','insertion',descending=False)])

    print('\nSort by weight descending (bubble):')
    print([r['client_name'] for r in sort_records('weight_kg','bubble',descending=True)])

    print('\nStatistics:')
    pprint(compute_statistics())

    print('\nFilter weight 65-85:')
    print([r['client_name'] for r in filter_weight_range(65,85)])

    print('\nSave state:')
    print(save_state())

    print('\nTest run complete.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
