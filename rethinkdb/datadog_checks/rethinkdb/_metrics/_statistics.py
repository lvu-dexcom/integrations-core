# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
"""
Collect metrics about system statistics.

See: https://rethinkdb.com/docs/system-stats/
"""

from __future__ import absolute_import

import logging
from typing import Iterator

import rethinkdb

from .._queries import query_cluster_stats, query_replicas_with_stats, query_servers_with_stats, query_tables_with_stats
from .._types import Metric

logger = logging.getLogger(__name__)


def collect_cluster_statistics(conn):
    # type: (rethinkdb.net.Connection) -> Iterator[Metric]
    stats = query_cluster_stats(conn)
    logger.debug('cluster_statistics stats=%r', stats)

    query_engine = stats['query_engine']

    yield {
        'type': 'gauge',
        'name': 'rethinkdb.stats.cluster.queries_per_sec',
        'value': query_engine['queries_per_sec'],
        'tags': [],
    }

    yield {
        'type': 'gauge',
        'name': 'rethinkdb.stats.cluster.read_docs_per_sec',
        'value': query_engine['read_docs_per_sec'],
        'tags': [],
    }

    yield {
        'type': 'gauge',
        'name': 'rethinkdb.stats.cluster.written_docs_per_sec',
        'value': query_engine['written_docs_per_sec'],
        'tags': [],
    }


def collect_server_statistics(conn):
    # type: (rethinkdb.net.Connection) -> Iterator[Metric]
    for server, stats in query_servers_with_stats(conn):
        logger.debug('server_statistics server=%r, stats=%r', server, stats)

        name = server['name']
        server_tags = server['tags']
        query_engine = stats['query_engine']

        tags = ['server:{}'.format(name)] + server_tags

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.server.client_connections',
            'value': query_engine['client_connections'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.server.clients_active',
            'value': query_engine['clients_active'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.server.queries_per_sec',
            'value': query_engine['queries_per_sec'],
            'tags': tags,
        }

        yield {
            'type': 'monotonic_count',
            'name': 'rethinkdb.stats.server.queries_total',
            'value': query_engine['queries_total'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.server.read_docs_per_sec',
            'value': query_engine['read_docs_per_sec'],
            'tags': tags,
        }

        yield {
            'type': 'monotonic_count',
            'name': 'rethinkdb.stats.server.read_docs_total',
            'value': query_engine['read_docs_total'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.server.written_docs_per_sec',
            'value': query_engine['written_docs_per_sec'],
            'tags': tags,
        }

        yield {
            'type': 'monotonic_count',
            'name': 'rethinkdb.stats.server.written_docs_total',
            'value': query_engine['written_docs_total'],
            'tags': tags,
        }


def collect_table_statistics(conn):
    # type: (rethinkdb.net.Connection) -> Iterator[Metric]
    for table, stats in query_tables_with_stats(conn):
        logger.debug('table_statistics table=%r, stats=%r', table, stats)

        name = table['name']
        database = table['db']
        query_engine = stats['query_engine']

        tags = ['table:{}'.format(name), 'database:{}'.format(database)]

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table.read_docs_per_sec',
            'value': query_engine['read_docs_per_sec'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table.written_docs_per_sec',
            'value': query_engine['written_docs_per_sec'],
            'tags': tags,
        }


def collect_replica_statistics(conn):
    # type: (rethinkdb.net.Connection) -> Iterator[Metric]
    for table, server, stats in query_replicas_with_stats(conn):
        logger.debug('replica_statistics table=%r server=%r stats=%r', table, server, stats)

        database = stats['db']
        server_name = server['name']
        table_name = table['name']
        server_tags = server['tags']
        query_engine = stats['query_engine']
        storage_engine = stats['storage_engine']

        tags = [
            'table:{}'.format(table_name),
            'database:{}'.format(database),
            'server:{}'.format(server_name),
        ] + server_tags

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.read_docs_per_sec',
            'value': query_engine['read_docs_per_sec'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.read_docs_total',
            'value': query_engine['read_docs_total'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.written_docs_per_sec',
            'value': query_engine['written_docs_per_sec'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.written_docs_total',
            'value': query_engine['written_docs_total'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.cache.in_use_bytes',
            'value': storage_engine['cache']['in_use_bytes'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.disk.read_bytes_per_sec',
            'value': storage_engine['disk']['read_bytes_per_sec'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.disk.read_bytes_total',
            'value': storage_engine['disk']['read_bytes_total'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.disk.written_bytes_per_sec',
            'value': storage_engine['disk']['written_bytes_per_sec'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.disk.written_bytes_total',
            'value': storage_engine['disk']['written_bytes_total'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.disk.metadata_bytes',
            'value': storage_engine['disk']['space_usage']['metadata_bytes'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.disk.data_bytes',
            'value': storage_engine['disk']['space_usage']['data_bytes'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.disk.garbage_bytes',
            'value': storage_engine['disk']['space_usage']['garbage_bytes'],
            'tags': tags,
        }

        yield {
            'type': 'gauge',
            'name': 'rethinkdb.stats.table_server.disk.preallocated_bytes',
            'value': storage_engine['disk']['space_usage']['preallocated_bytes'],
            'tags': tags,
        }