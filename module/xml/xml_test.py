from xml.etree.ElementTree import ElementTree

tree = ElementTree()
tree.parse("test.xml")
root = tree.getroot()
print(root.tag)
print(root[0].tag)
print(root[0].attrib)
schools = root.getchildren() 
for school in schools:
    print(school.get("Name"))
    classes = school.findall("Class")
    for mclass in classes:
        print(mclass.items())
        print(mclass.keys())
        print(mclass.attrib["Id"])
        math = mclass.find("Student").find("Scores").find("Math")
        print(math.text)
        math.set("teacher", "bada")
        
tree.write("new.xml")
