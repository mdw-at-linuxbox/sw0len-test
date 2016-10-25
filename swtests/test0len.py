from . import ( makeconnection, )

container1 = "box"
container2 = "container"
myobj = "myobj"

# trivial test - proof of concept
def test_trivial_make_delete_container():
 c = makeconnection()
 e = c.put_container(container1)
 e = c.delete_container(container1)
def test_make_NZ_object():
 c = makeconnection()
 e = c.put_container(container2)
 e = c.put_object(container2, myobj + "/00000001", "a short bit of text")
 e = c.put_object(container2, myobj + "/00000002")
 e = c.put_object(container2, myobj,
   headers={'X-Object-Manifest': container2 + "/" + myobj + "/"})
 (rh,rc) = c.get_object(container2, myobj, headers = {'Range': 'bytes=5-20'})

def test_bad_cleanup_fixmefixmefixme():
 c = makeconnection()
 e = c.delete_container(container2)
