#!/usr/bin/env bash
# Use this script to test if a given TCP host/port are available

WAITFORIT_cmdname=${0##*/}
WAITFORIT_waittime=15
WAITFORIT_interval=1
WAITFORIT_timeout=15
WAITFORIT_cmd=""
WAITFORIT_host=""
WAITFORIT_port=""

# display usage
usage()
{
    cat << USAGE >&2
Usage:
    $WAITFORIT_cmdname host:port [-s] [-t timeout] [-- command args]
    -h HOST | --host=HOST       Host or IP under test
    -p PORT | --port=PORT       TCP port under test
                                Alternatively, you specify the host and port as host:port
    -s | --strict               Only execute subcommand if the test succeeds
    -q | --quiet                Don't output any status messages
    -t TIMEOUT | --timeout=TIMEOUT
                                Timeout in seconds, zero for no timeout
    -- COMMAND ARGS             Execute command with args after the test finishes
USAGE
    exit 1
}

wait_for()
{
    if [ "$WAITFORIT_timeout" -gt 0 ]; then
        echo >&2 "$WAITFORIT_cmdname: waiting $WAITFORIT_timeout seconds for $WAITFORIT_host:$WAITFORIT_port"
    else
        echo >&2 "$WAITFORIT_cmdname: waiting for $WAITFORIT_host:$WAITFORIT_port without a timeout"
    fi
    start_ts=$(date +%s)
    while :
    do
        if [ "$WAITFORIT_isquiet" -eq 0 ]; then
            (echo > /dev/tcp/$WAITFORIT_host/$WAITFORIT_port) >/dev/null 2>&1
        else
            (echo > /dev/tcp/$WAITFORIT_host/$WAITFORIT_port) >/dev/null 2>&1
        fi
        result=$?
        if [ $result -eq 0 ] ; then
            end_ts=$(date +%s)
            echo >&2 "$WAITFORIT_cmdname: $WAITFORIT_host:$WAITFORIT_port is available after $((end_ts - start_ts)) seconds"
            break
        fi
        sleep 1
    done
    return $result
}

WAITFORIT_isquiet=0

while [ $# -gt 0 ]
do
    case "$1" in
        *:* )
        WAITFORIT_host=$(echo $1 | cut -d : -f 1)
        WAITFORIT_port=$(echo $1 | cut -d : -f 2)
        shift 1
        ;;
        -q | --quiet)
        WAITFORIT_isquiet=1
        shift 1
        ;;
        -s | --strict)
        WAITFORIT_strict=1
        shift 1
        ;;
        -h)
        WAITFORIT_host="$2"
        if [ "$WAITFORIT_host" == "" ]; then break; fi
        shift 2
        ;;
        --host=*)
        WAITFORIT_host="${1#*=}"
        shift 1
        ;;
        -p)
        WAITFORIT_port="$2"
        if [ "$WAITFORIT_port" == "" ]; then break; fi
        shift 2
        ;;
        --port=*)
        WAITFORIT_port="${1#*=}"
        shift 1
        ;;
        -t)
        WAITFORIT_timeout="$2"
        if [ "$WAITFORIT_timeout" == "" ]; then break; fi
        shift 2
        ;;
        --timeout=*)
        WAITFORIT_timeout="${1#*=}"
        shift 1
        ;;
        --)
        shift
        WAITFORIT_cmd="$@"
        break
        ;;
        --help)
        usage
        ;;
        *)
        echo >&2 "Unknown argument: $1"
        usage
        ;;
    esac
done

if [ "$WAITFORIT_host" == "" -o "$WAITFORIT_port" == "" ]; then
    echo >&2 "Error: you need to provide a host and port to test."
    usage
fi

wait_for

WAITFORIT_RESULT=$?

if [ "$WAITFORIT_cmd" != "" ]; then
    if [ $WAITFORIT_RESULT -ne 0 -a $WAITFORIT_strict -eq 1 ]; then
        echo >&2 "$WAITFORIT_cmdname: strict mode, refusing to execute subprocess"
        exit $WAITFORIT_RESULT
    fi
    exec $WAITFORIT_cmd
else
    exit $WAITFORIT_RESULT
fi
