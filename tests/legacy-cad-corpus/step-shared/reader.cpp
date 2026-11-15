// Adapted from CAD test/owned-step-worker/ledger-reader.cpp.
// Separate same-OCCT reader build: roundtrip, not an independent implementation.
#include <cmath>
#include "ownedTopologyV1.hpp"
#include <STEPControl_Reader.hxx>
#include <BRepClass3d_SolidClassifier.hxx>
#include <BRepGProp.hxx>
#include "ownedMassPropertiesV1.hpp"
#include <BRepBndLib.hxx>
#include <GProp_GProps.hxx>
#include <Bnd_Box.hxx>
#include <TColStd_SequenceOfAsciiString.hxx>
#include <fstream>
#include <iostream>
#include <vector>
#include <array>
#include <iomanip>
struct Probe{gp_Pnt p;TopAbs_State state;};
struct Fixture{const char*name;double volume;std::array<double,6> bounds;int solids,shells;std::vector<Probe> probes;};
void check(bool b,const char*m){if(!b)throw std::runtime_error(m);}
const char* stateName(TopAbs_State s){return s==TopAbs_IN?"inside":s==TopAbs_OUT?"outside":s==TopAbs_ON?"boundary":"unknown";}
TopAbs_State classify(const TopoDS_Shape&s,const gp_Pnt&p){bool on=false;for(TopExp_Explorer i(s,TopAbs_SOLID);i.More();i.Next()){BRepClass3d_SolidClassifier c(i.Current(),p,1e-7);if(c.State()==TopAbs_IN)return TopAbs_IN;if(c.State()==TopAbs_ON)on=true;check(c.State()!=TopAbs_UNKNOWN,"unknown classifier");}return on?TopAbs_ON:TopAbs_OUT;}
int main(int argc,char**argv){try{check(argc==2,"dir required");const std::string dir=argv[1];const double pi=std::acos(-1.);const double origin=1000000,dx=(origin+1e-6)-origin,dy=(origin+2e-6)-origin,dz=(origin+3e-6)-origin;
 std::vector<Fixture> fixtures;
 const std::vector<Probe> plate={{{50,25,10},TopAbs_OUT},{{5,5,10},TopAbs_IN},{{0,25,10},TopAbs_ON},{{101,25,10},TopAbs_OUT}};
 fixtures.push_back({"plate-hole",100000-500*pi,{0,0,0,100,50,20},1,1,plate});
 fixtures.push_back({"plate-hole-clean",100000-500*pi,{0,0,0,100,50,20},1,1,plate});
 fixtures.push_back({"plate-hole-menu",100000-500*pi,{0,0,0,100,50,20},1,1,plate});
 fixtures.push_back({"plate-hole-reedited",100000-980*pi,{0,0,0,100,50,20},1,1,plate});
 for(int edited=0;edited<2;edited++){const double depth=edited?25:20;auto probes=plate;for(auto &p:probes)p.p.SetZ(depth/2);probes.push_back({gp_Pnt(125,10,15),TopAbs_IN});probes.push_back({gp_Pnt(110,10,15),TopAbs_OUT});fixtures.push_back({edited?"two-outputs-reedited":"two-outputs",5000*depth-25*pi*depth+6000,{0,0,0,130,50,30},2,2,probes});if(!edited)fixtures.push_back({"two-outputs-clean",5000*depth-25*pi*depth+6000,{0,0,0,130,50,30},2,2,probes});}
 for(int edited=0;edited<2;edited++){const double depth=edited?25:20;std::vector<Probe> probes;for(int row=1;row<=4;row++)for(int col=1;col<=8;col++)probes.push_back({gp_Pnt(10*col,10*row,depth/2),TopAbs_OUT});probes.push_back({gp_Pnt(5,5,depth/2),TopAbs_IN});probes.push_back({gp_Pnt(0,25,depth/2),TopAbs_ON});probes.push_back({gp_Pnt(101,25,depth/2),TopAbs_OUT});fixtures.push_back({edited?"32-holes-reedited":"32-holes",5000*depth-128*pi*depth,{0,0,0,100,50,depth},1,1,probes});if(!edited)fixtures.push_back({"32-holes-clean",5000*depth-128*pi*depth,{0,0,0,100,50,depth},1,1,probes});}

 for(auto&f:fixtures){const std::string label=f.name;const double z=f.bounds[5]/2;if(label.find("32-holes")==0){for(int row=1;row<=4;row++)for(int col=1;col<=8;col++){f.probes.push_back({gp_Pnt(10*col+2,10*row,z),TopAbs_ON});f.probes.push_back({gp_Pnt(10*col+2.5,10*row,z),TopAbs_IN});}}else{const double r=label=="plate-hole-reedited"?7:5;const double plateZ=label.find("two-outputs")==0?(label=="two-outputs-reedited"?12.5:10):z;f.probes.push_back({gp_Pnt(50+r,25,plateZ),TopAbs_ON});f.probes.push_back({gp_Pnt(50+r+.5,25,plateZ),TopAbs_IN});}std::ifstream file(dir+"/"+f.name+".step",std::ios::binary);check(file.good(),"open step");STEPControl_Reader reader;check(reader.ReadStream(f.name,file)==IFSelect_RetDone,"read step");TColStd_SequenceOfAsciiString length,plane,solid;reader.FileUnits(length,plane,solid);check(length.Length()>0,"declared units");for(int i=1;i<=length.Length();i++)check(length(i)=="millimetre","millimetre reader units");reader.SetSystemLengthUnit(1.0);const int roots=reader.NbRootsForTransfer();check(roots>0&&reader.TransferRoots()>0,"transfer roots");const TopoDS_Shape shape=reader.OneShape();check(!shape.IsNull()&&BRepCheck_Analyzer(shape).IsValid(),"read validity");const e0::owned_topology_v1::Maps maps(shape);check(maps.solids.Extent()==f.solids,"solid count");TopTools_IndexedMapOfShape shells;TopExp::MapShapes(shape,TopAbs_SHELL,shells);check(shells.Extent()==f.shells,"shell count");GProp_GProps coarse,props;BRepGProp::VolumeProperties(shape,coarse);const double achieved=e0::owned_mass_properties_v1::volumeProperties(shape,props);const double tolerance=f.volume<1e-12?f.volume*1e-6:1e-6;check(std::isfinite(props.Mass())&&props.Mass()>0&&std::abs(props.Mass()-f.volume)<=tolerance,"analytic adaptive volume");Bnd_Box box;BRepBndLib::AddOptimal(shape,box,false,false);double b[6];box.Get(b[0],b[1],b[2],b[3],b[4],b[5]);for(int i=0;i<6;i++)check(std::isfinite(b[i])&&std::abs(b[i]-f.bounds[i])<=1e-6,"analytic bounds");
 std::cout<<"OBS {\"label\":\""<<f.name<<"\",\"status\":\"PASS\",\"reader\":\"same-OCCT-separate-build\",\"roots\":"<<roots<<",\"solids\":"<<maps.solids.Extent()<<",\"shells\":"<<shells.Extent()<<",\"unit\":\"millimeter\",\"volume\":"<<std::setprecision(17)<<props.Mass()<<",\"coarseVolume\":"<<coarse.Mass()<<",\"achievedIntegrationEstimate\":"<<achieved<<",\"catalog\":"<<e0::owned_topology_v1::catalog(shape)<<",\"bounds\":[";for(int i=0;i<6;i++)std::cout<<(i?",":"")<<b[i];std::cout<<"],\"points\":[";for(std::size_t i=0;i<f.probes.size();i++){const auto&p=f.probes[i];const TopAbs_State actual=classify(shape,p.p);check(actual==p.state,"analytic point");std::cout<<(i?",":"")<<"{\"point\":["<<p.p.X()<<","<<p.p.Y()<<","<<p.p.Z()<<"],\"classification\":\""<<stateName(actual)<<"\"}";}std::cout<<"]}\n";
 }return 0;}catch(const Standard_Failure&e){std::cerr<<"NATIVE_FAIL "<<e.GetMessageString()<<"\n";}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<"\n";}return 1;}
