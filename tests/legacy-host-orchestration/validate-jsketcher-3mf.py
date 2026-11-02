"""Independent local reader: install lib3mf==2.5.0 in an isolated venv."""
import sys
import lib3mf
w=lib3mf.get_wrapper();m=w.CreateModel();r=m.QueryReader('3mf');r.SetStrictModeActive(True);r.ReadFromFile(sys.argv[1])
assert r.GetWarningCount()==0
assert m.GetUnit()==lib3mf.ModelUnit.MilliMeter and m.GetBuildItems().Count()==2
it=m.GetMeshObjects();assert it.Count()==2
while it.MoveNext():
    obj=it.GetCurrentMeshObject()
    assert obj.IsValid() and obj.IsManifoldAndOriented() and obj.GetTriangleCount()==12
it=m.GetBaseMaterialGroups();assert it.Count()==1;it.MoveNext();group=it.GetCurrentBaseMaterialGroup()
ids=group.GetAllPropertyIDs();assert len(ids)==1 and group.GetName(ids[0])=='PLA'
color=group.GetDisplayColor(ids[0]);assert (color.Red,color.Green,color.Blue,color.Alpha)==(255,0,0,255)
print('PASS: independent strict reader, two oriented boxes, PLA material and color')
