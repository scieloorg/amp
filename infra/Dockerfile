FROM python:3.7.4-alpine AS build-py
WORKDIR /code
RUN apk update && apk add gcc musl-dev && \
    pip install --no-cache-dir cython
COPY server/*.py ./
RUN mkdir -p build dist && \
    for f in *.py ; do \
        cython -3 -o "build/${f%.py}.c" "$f" && \
        gcc -Wall \
            -Wno-unused-result -Wsign-compare -Wstrict-prototypes \
            -DNDEBUG -fwrapv -fPIC -O3 \
            -DTHREAD_STACK_SIZE=0x100000 \
            -I/usr/local/include/python3.7m \
            -c "build/${f%.py}.c" \
            -o "build/${f%.py}.o" && \
        gcc -shared "build/${f%.py}.o" \
            -L/usr/local/lib -lpython3.7m \
            -o "dist/${f%.py}.so" ; \
    done


FROM python:3.7.4-alpine
COPY server/requirements.txt .
RUN apk update && \
    apk add openblas libxml2 libxslt libstdc++ && \
    apk add --virtual .build-deps gcc g++ make \
      musl-dev openblas-dev libxml2-dev libxslt-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps
COPY --from=build-py /code/dist/* ./
COPY infra/run.sh *.dict *.model ./
CMD [ "./run.sh" ]
