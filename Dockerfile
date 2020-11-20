# thanks @MechMaster48
FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mv pybotrc /root/.pybotrc

# for example: docker run -it <your image name> --nick argbot --server irc.yourserver.com --channels "#channel1, #channel2"
ENTRYPOINT [ "python3", "./pybot.py", "-d" ]
