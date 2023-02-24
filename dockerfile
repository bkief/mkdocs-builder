from python:3.11-slim-bullseye

# Set build directory
WORKDIR /tmp
COPY  setup.py s3docs-upload/* requirements.txt ./

# Install dependencies
RUN pip install \
    -r requirements.txt \
    && python setup.py bdist_wheel \ 
    && pip install dist/s3docs_upload*.whl \
    && pip cache purge \
    && mkdir /docs && chmod -R 777 /docs && rm -rf /tmp/*

#RUN pip install pipdeptree && pipdeptree
#RUN pip list --format freeze | awk -F = {'print $1'} | xargs pip show | grep -E 'Location:|Name:' | cut -d ' ' -f 2 | paste -d ' ' - - | awk '{gsub("-","_",$1); print $2 "/" tolower($1)}' | xargs du -sh 2> /dev/null | sort -h

# Set working directory
WORKDIR /docs

# Expose MkDocs development server port
EXPOSE 8000

# Start development server by default
#ENTRYPOINT ["mkdocs"]
#CMD ["serve", "--dev-addr=0.0.0.0:8000"]
