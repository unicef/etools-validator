#!/usr/bin/env bash
curl --user ${CIRCLE_TOKEN}: \
    --request POST \
    --form revision=b6989c3410ee204551fa84a0ef34af630f7bf91e \
    --form config=@config.yml \
    --form notify=false \
        https://circleci.com/api/v1.1/project/github/unicef/etools-validator/tree/master
