##
# Copyright (c) 2016 MagicStack Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import asyncpg

from edgedb.lang.schema import delta as s_delta
from edgedb.lang.schema import deltas as s_deltas

from edgedb.server import query as edgedb_query

from edgedb.lang.common.debug import debug


@debug
async def execute_plan(plan, backend):
    if isinstance(plan, s_deltas.DeltaCommand):
        return await backend.run_delta_command(plan)

    elif isinstance(plan, s_delta.Command):
        return await backend.run_ddl_command(plan)

    elif isinstance(plan, edgedb_query.Query):
        """LOG [sql] SQL QUERY
        print(plan.text)
        """

        try:
            ps = await backend.connection.prepare(plan.text)
            return [r[0] for r in await ps.fetch()]

        except asyncpg.PostgresError as e:
            _error = await backend.translate_pg_error(plan, e)
            if _error is not None:
                raise _error from e
            else:
                raise

    else:
        raise exceptions.InternalError('unexpected plan: {!r}'.format(plan))
