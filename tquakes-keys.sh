#!/bin/bash
. configuration
cp --no-preserve=mode,ownership stations/authorized_keys $HOMEDIR/$TQUSER/.ssh/authorized_keys
