FROM python:3.8-alpine
RUN pip install sketchfab==0.0.8
ENTRYPOINT ["sketchfab"]
