def read():
    response = yield "First sentence"
    print("Response "+str(response))

gen_obj = read()
print(gen_obj.send(None))
print(gen_obj.send("Hello!"))
