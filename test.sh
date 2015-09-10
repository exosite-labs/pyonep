#!/bin/bash

function test_current_env() {
    nosetests --verbose --with-coverage --cover-erase --cover-package=pyonep --cover-package=examples
}

function test_all_envs() {
    # Kick off tests
    for py_version in py26 py27 py32 py33 py34; do
        echo "Starting test for ${py_version}"
        sed "s/{envname}/${py_version}/g" tox.ini > "tox_${py_version}.ini"
	(tox -e "$py_version" -c "tox_${py_version}.ini" -- --with-coverage --cover-erase --cover-package=pyonep --cover-package=examples > "${TMPDIR}/tox_output_${py_version}" 2>&1 || echo "${py_version}" >> tox_failures) &
    done

    # Wait for all the versions to finish testing
    echo "Waiting for tests to finish"
    for job in $(jobs -p); do
        wait "$job"
    done

    # Report results
    if [ -e tox_failures ]; then
        echo "Tests failed for these versions:"
        cat tox_failures
        for failed_version in $(cat tox_failures); do
            echo "Output for $failed_version:"
            echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            cat ${TMPDIR}/tox_output_${failed_version}
        done
        exit 1
    else
        echo "All tests passed. Congratulations! :)"
    fi
}


rm -f tox_failures tox_py*.ini
if [ -z "$TMPDIR" ]; then
    export TMPDIR=/tmp
fi
if [ "$1" == "full" ]; then
    test_all_envs
else
    test_current_env
fi
