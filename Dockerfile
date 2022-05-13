FROM ubuntu:latest
MAINTAINER Luca Napoletano (lnapo94@gmail.com)

# Update packages
RUN apt-get update && apt-get -y upgrade

# Install curl
RUN apt-get -y install curl

# Install Python 3.10
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update
RUN apt install python3.10 -y
RUN apt install python3-pip -y

# Install Node
RUN curl -sL https://deb.nodesource.com/setup_18.x  | bash -
RUN apt-get -y install nodejs

# Install SFDX
RUN npm install sfdx-cli --global 

# Install PYDX
RUN python3 -m pip install https://files.pythonhosted.org/packages/8e/42/043f67bd1e5a61c69a760eda618102adf850fbf52782750be22bc2b66951/Python%20SFDX%20Toolkit-0.0.1.tar.gz