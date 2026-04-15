FROM registry.access.redhat.com/ubi9/ubi:latest


####### PYTHON 3

# Install Python 3 and pip
RUN dnf -y install python3.11 python3.11-pip && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Set Python 3 as default
RUN alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    alternatives --set python3 /usr/bin/python3.11

RUN alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1 && \
    alternatives --set pip3 /usr/bin/pip3.11

# Verify installation
RUN python3 --version && pip3 --version


####### JAVA OPENJDK21

RUN dnf -y install java-21-openjdk-devel && \
    dnf clean all && \
    rm -rf /var/cache/dnf

ENV JAVA_HOME="/usr/lib/jvm/java-21"
ENV JAVA_VENDOR="openjdk"
ENV JAVA_VERSION="21"
ENV PATH="$JAVA_HOME/bin:$PATH"


####### MAVEN 3.9

RUN dnf install -y maven-openjdk21 && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Verify installations
RUN java -version && python3 --version && mvn --version


####### PERL

RUN dnf -y install perl && \
    dnf clean all && \
    rm -rf /var/cache/dnf


####### COPY CODE

# Set working directory
WORKDIR /app

# Copy application code (if any)
COPY . /app

# Set maven settings.xml that is aware of all the necessary Red Hat repositories.
RUN ls -la
RUN mkdir -p ~/.m2
RUN mv settings.xml ~/.m2/settings.xml


######## EMPROGEN INSTALL

RUN pip3 install -r enterprise-application-code-generator/python/requirements.txt
RUN mvn -f enterprise-application-code-generator/java/pom.xml clean install 

CMD ["/bin/bash"]