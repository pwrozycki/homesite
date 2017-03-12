#!/bin/sh

function bootstrap_postgres() {
    echo "Creating a new PostgreSQL database cluster"

    if [ -d "${PGDATA}/base" ] ; then
        echo "${PGDATA}/base already exists"
        return 1
    fi

    mkdir -p "${PGDATA}"  2>/dev/null
    chown -Rf postgres:postgres "${PGDATA}"
    chmod 0700 "${PGDATA}"
    su -c "/usr/bin/initdb --pgdata ${PGDATA}" postgres
    res=$?
    cp -v /pg_hba.conf ${PGDATA}/
    chown postgres:postgres ${PGDATA}/pg_hba.conf

    return $res
}

function create_user() {
    su-exec postgres pg_ctl start -D $PGDATA -w
    su-exec postgres psql <<EOF
        CREATE ROLE $DBUSER LOGIN CREATEDB PASSWORD '$DBPASSWORD';
        CREATE DATABASE $DBNAME OWNER $DBUSER;
EOF
    su-exec postgres pg_ctl stop -D $PGDATA
}

bootstrap_postgres
create_user
su-exec postgres postgres -D ${PGDATA} -h 0.0.0.0