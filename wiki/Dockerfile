FROM ruby:3.0

RUN apt-get update && \
    # pip to install docutils, cmake to build github-linguist
    apt-get install -y python3-pip cmake && \
    python3 -m pip install docutils && \
    apt-get remove -y python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY Gemfile Gemfile.lock ./
RUN bundle install

RUN apt-get remove cmake && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY fetcher.rb .

ENTRYPOINT [ "./fetcher.rb" ]
