FROM public.ecr.aws/lambda/python:3.9
RUN python3 -m pip install --upgrade pip
COPY app/requirements.in .
RUN pip3 install -r requirements.in --target "${LAMBDA_TASK_ROOT}" \
        --platform manylinux2014_aarch64 \
        --implementation cp \
        --only-binary=:all: \
        --upgrade
COPY app/ ${LAMBDA_TASK_ROOT}/app/
RUN ls -la ${LAMBDA_TASK_ROOT}
CMD [ "app.app.handler" ]