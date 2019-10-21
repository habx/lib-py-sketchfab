FROM python:3.8-alpine
RUN pip install sketchfab==0.0.6
ENTRYPOINT ["sketchfab"]
