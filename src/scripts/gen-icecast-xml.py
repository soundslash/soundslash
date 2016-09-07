import csv
import string, random
from random import randrange

def main():
    servers = 100
    out = "icecast.xml"

    names = parse_stream_names("baby-names.csv")
    mount_points = ""
    for i in range(servers):
        rand = randrange(len(names))
        name = names[rand]
        del names[rand]
        mount_points += server(name.lower())

    f = open('icecast.xml.tpl', 'r')
    template = f.read()
    f.close()
    out_data = template.replace("### INSERT MOUNT POINTS ###", mount_points)

    f = open(out, 'w')
    f.write(out_data)
    f.close()

def parse_stream_names(filename):
    names = []
    with open(filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            if (row[3] == "girl"):
                names.append(row[1])
    return names

def gen_pass(length):
    return ''.join(random.choice(string.lowercase+"0123456789") for x in range(length))

def server(name):
    server = """\n    <mount>
        <mount-name>/{0}.ogg</mount-name>
        <password>{1}</password>
        <max-listeners>8</max-listeners>
        <authentication type="url">
        <option name="mount_add" value="http://127.0.0.1:8888/mount_add"/>
        <option name="mount_remove" value="http://127.0.0.1:8888/mount_remove"/>
        <option name="listener_add" value="http://127.0.0.1:8888/listener_add"/>
        <option name="listener_remove" value="http://127.0.0.1:8888/listener_remove"/>
        <option name="auth_header" value="icecast-auth-user: 1"/>
        </authentication>
    </mount>\n""".format(name, gen_pass(8))
    return server


if __name__ == "__main__":
    main()
