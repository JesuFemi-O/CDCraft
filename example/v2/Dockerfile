FROM debezium/connect:3.0.0.Final

USER kafka

ENV PLUGIN_DIR=/kafka/connect/plugins

RUN mkdir -p $PLUGIN_DIR

ENV AUTH_LIB_DIR=/kafka/libs

RUN curl -sL --retry 5 https://packages.confluent.io/confluent-hub-client/confluent-hub-client-latest.tar.gz -o /tmp/confluent-hub-client.tar.gz && \
    mkdir -p /usr/local/confluent-hub-client && \
    tar -xzf /tmp/confluent-hub-client.tar.gz -C /usr/local/confluent-hub-client --strip-components=1 && \
    rm /tmp/confluent-hub-client.tar.gz && \
    ln -s /usr/local/confluent-hub-client/bin/confluent-hub /usr/local/bin/confluent-hub


# Install Confluent Secrets Manager Plugin
RUN confluent-hub install --no-prompt --component-dir $PLUGIN_DIR confluentinc/csid-secrets-provider-aws:latest

RUN curl -L -o $PLUGIN_DIR/kafka-connect-avro-converter.jar \
    https://packages.confluent.io/maven/io/confluent/kafka-connect-avro-converter/7.3.0/kafka-connect-avro-converter-7.3.0.jar && \
    curl -L -o $PLUGIN_DIR/kafka-connect-avro-data.jar \
    https://packages.confluent.io/maven/io/confluent/kafka-connect-avro-data/7.3.0/kafka-connect-avro-data-7.3.0.jar && \
    curl -L -o $PLUGIN_DIR/kafka-avro-serializer.jar \
    https://packages.confluent.io/maven/io/confluent/kafka-avro-serializer/7.3.0/kafka-avro-serializer-7.3.0.jar && \
    curl -L -o $PLUGIN_DIR/kafka-schema-serializer.jar \
    https://packages.confluent.io/maven/io/confluent/kafka-schema-serializer/7.3.0/kafka-schema-serializer-7.3.0.jar && \
    curl -L -o $PLUGIN_DIR/kafka-schema-converter.jar \
    https://packages.confluent.io/maven/io/confluent/kafka-schema-converter/7.3.0/kafka-schema-converter-7.3.0.jar && \
    curl -L -o $PLUGIN_DIR/kafka-schema-registry-client.jar \
    https://packages.confluent.io/maven/io/confluent/kafka-schema-registry-client/7.3.0/kafka-schema-registry-client-7.3.0.jar && \
    curl -L -o $PLUGIN_DIR/common-config.jar \
    https://packages.confluent.io/maven/io/confluent/common-config/7.3.0/common-config-7.3.0.jar && \
    curl -L -o $PLUGIN_DIR/common-utils.jar \
    https://packages.confluent.io/maven/io/confluent/common-utils/7.3.0/common-utils-7.3.0.jar && \
    curl -L -o $PLUGIN_DIR/avro.jar \
    https://repo1.maven.org/maven2/org/apache/avro/avro/1.10.2/avro-1.10.2.jar && \
    curl -L -o $PLUGIN_DIR/commons-compress.jar \
    https://repo1.maven.org/maven2/org/apache/commons/commons-compress/1.21/commons-compress-1.21.jar && \
    curl -L -o $PLUGIN_DIR/failureaccess.jar \
    https://repo1.maven.org/maven2/com/google/guava/failureaccess/1.0.1/failureaccess-1.0.1.jar && \
    curl -L -o $PLUGIN_DIR/guava.jar \
    https://repo1.maven.org/maven2/com/google/guava/guava/31.1-jre/guava-31.1-jre.jar && \
    curl -L -o $PLUGIN_DIR/minimal-json.jar \
    https://repo1.maven.org/maven2/com/eclipsesource/minimal-json/minimal-json/0.9.5/minimal-json-0.9.5.jar && \
    curl -L -o $PLUGIN_DIR/re2j.jar \
    https://repo1.maven.org/maven2/com/google/re2j/re2j/1.3/re2j-1.3.jar && \
    curl -L -o $PLUGIN_DIR/slf4j-api.jar \
    https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.32/slf4j-api-1.7.32.jar && \
    curl -L -o $PLUGIN_DIR/snakeyaml.jar \
    https://repo1.maven.org/maven2/org/yaml/snakeyaml/1.30/snakeyaml-1.30.jar && \
    curl -L -o $PLUGIN_DIR/swagger-annotations.jar \
    https://repo1.maven.org/maven2/io/swagger/swagger-annotations/1.6.4/swagger-annotations-1.6.4.jar && \
    curl -L -o $PLUGIN_DIR/jackson-databind.jar \
    https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-databind/2.13.3/jackson-databind-2.13.3.jar && \
    curl -L -o $PLUGIN_DIR/jackson-core.jar \
    https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-core/2.13.3/jackson-core-2.13.3.jar && \
    curl -L -o $PLUGIN_DIR/jackson-annotations.jar \
    https://repo1.maven.org/maven2/com/fasterxml/jackson/core/jackson-annotations/2.13.3/jackson-annotations-2.13.3.jar && \
    curl -L -o $PLUGIN_DIR/jackson-dataformat-csv.jar \
    https://repo1.maven.org/maven2/com/fasterxml/jackson/dataformat/jackson-dataformat-csv/2.13.3/jackson-dataformat-csv-2.13.3.jar && \
    curl -L -o $PLUGIN_DIR/logredactor.jar \
    https://repo1.maven.org/maven2/io/confluent/logredactor/7.3.0/logredactor-7.3.0.jar && \
    curl -L -o $PLUGIN_DIR/logredactor-metrics.jar \
    https://repo1.maven.org/maven2/io/confluent/logredactor-metrics/7.3.0/logredactor-metrics-7.3.0.jar \
    curl -L -o $PLUGIN_DIR/guava-31.0.1 \
    https://repo1.maven.org/maven2/com/google/guava/guava/31.0.1-jre/guava-31.0.1-jre.jar \
    curl -L -o $AUTH_LIB_DIR/aws-msk-iam-auth-2.2.0-all.jar \
    https://github.com/aws/aws-msk-iam-auth/releases/download/v2.2.0/aws-msk-iam-auth-2.2.0-all.jar
    # curl -L -o $PLUGIN_DIR/aws-config-provider \
    # https://github.com/aws-samples/msk-config-providers/releases/download/r0.3.1/msk-config-providers-0.3.1-all.jar


RUN curl --create-dirs -LO --output-dir /tmp/connector https://github.com/aiven/s3-connector-for-apache-kafka/releases/download/v2.12.0/aiven-kafka-connect-s3-2.12.0.zip && \
    unzip -o /tmp/connector/aiven-kafka-connect-s3-2.12.0.zip -d /tmp/connector && \
    mv /tmp/connector/aiven-kafka-connect-s3-2.12.0 /kafka/connect/aiven-kafka-connect-s3 && \
    rm /tmp/connector/aiven-kafka-connect-s3-2.12.0.zip


RUN curl --create-dirs -LO --output-dir /tmp/bq-connector https://open-kconnect-connectors.s3.us-east-1.amazonaws.com/wepay-kafka-connect-bigquery-2.5.7.zip && \
    unzip -o /tmp/bq-connector/wepay-kafka-connect-bigquery-2.5.7.zip -d /tmp/bq-connector && \
    mv /tmp/bq-connector/wepay-kafka-connect-bigquery-2.5.7 /kafka/connect/wepay-kafka-connect-bigquery && \
    rm /tmp/bq-connector/wepay-kafka-connect-bigquery-2.5.7.zip


RUN curl --create-dirs -LO --output-dir /tmp/kafka-config-provider-aws https://open-kconnect-connectors.s3.us-east-1.amazonaws.com/jcustenborder-kafka-config-provider-aws-0.1.2.zip && \
    unzip -o /tmp/kafka-config-provider-aws/jcustenborder-kafka-config-provider-aws-0.1.2.zip -d /tmp/kafka-config-provider-aws && \
    mv /tmp/kafka-config-provider-aws/jcustenborder-kafka-config-provider-aws-0.1.2 /kafka/connect/jcustenborder-kafka-config-provider-aws-0.1.2 && \
    rm /tmp/kafka-config-provider-aws/jcustenborder-kafka-config-provider-aws-0.1.2.zip


# RUN curl --create-dirs -LO --output-dir /tmp/aws-config-provider https://github.com/aws-samples/msk-config-providers/releases/download/r0.1.0/msk-config-providers-0.1.0-with-dependencies.zip && \
#     unzip -o /tmp/aws-config-provider/msk-config-providers-0.1.0-with-dependencies.zip -d /tmp/aws-config-provider && \
#     mv /tmp/aws-config-provider/msk-config-providers-0.1.0-with-dependencies /kafka/connect/aws-config-providers && \
#     rm /tmp/aws-config-provider/msk-config-providers-0.1.0-with-dependencies.zip

# RUN curl --create-dirs -L -o /tmp/aws-config-provider/msk-config-providers-0.1.0-with-dependencies.zip \
#     https://github.com/aws-samples/msk-config-providers/releases/download/r0.1.0/msk-config-providers-0.1.0-with-dependencies.zip && \
#     unzip -o /tmp/aws-config-provider/msk-config-providers-0.1.0-with-dependencies.zip -d /tmp/aws-config-provider && \
#     rm /tmp/aws-config-provider/msk-config-providers-0.1.0-with-dependencies.zip && \
#     mv /tmp/aws-config-provider /kafka/connect/aws-config-providers

RUN curl --create-dirs -L -o /tmp/aws-config-provider/msk-config-providers-0.3.1-with-dependencies.zip \
    https://github.com/aws-samples/msk-config-providers/releases/download/r0.3.1/msk-config-providers-0.3.1-with-dependencies.zip && \
    unzip -o /tmp/aws-config-provider/msk-config-providers-0.3.1-with-dependencies.zip -d /tmp/aws-config-provider && \
    rm /tmp/aws-config-provider/msk-config-providers-0.3.1-with-dependencies.zip && \
    mv /tmp/aws-config-provider /kafka/connect/aws-config-providers

    # https://github.com/aws-samples/msk-config-providers/releases/download/r0.3.1/msk-config-providers-0.3.1-with-dependencies.zip
