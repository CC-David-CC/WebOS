#!/usr/bin/python3
"""Run inside the disposable live VM as the desktop account; export public UI assets."""
import ctypes as C
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import gi
os.environ['XDG_CURRENT_DESKTOP']='XFCE'
gi.require_version('Gtk','3.0')
from gi.repository import Gtk, GdkPixbuf
P=Path('/tmp/codiserver-preview-reference');shutil.rmtree(P,ignore_errors=True);(P/'assets/icons').mkdir(parents=True)
lib=C.CDLL('libgarcon-1.so.0');obj=C.CDLL('libgobject-2.0.so.0');glib=C.CDLL('libglib-2.0.so.0')
def f(lib,name,args,restype):
 fn=getattr(lib,name);fn.argtypes=args;fn.restype=restype;return fn
ptr=C.c_void_p
new=f(lib,'garcon_menu_new_applications',[],ptr)
load=f(lib,'garcon_menu_load',[ptr,ptr,ptr],C.c_int)
get_elements=f(lib,'garcon_menu_get_elements',[ptr],ptr)
name=f(lib,'garcon_menu_element_get_name',[ptr],C.c_char_p)
icon=f(lib,'garcon_menu_element_get_icon_name',[ptr],C.c_char_p)
visible=f(lib,'garcon_menu_element_get_visible',[ptr],C.c_int)
menu_type=f(lib,'garcon_menu_get_type',[],C.c_size_t)()
item_type=f(lib,'garcon_menu_item_get_type',[],C.c_size_t)()
separator_type=f(lib,'garcon_menu_separator_get_type',[],C.c_size_t)()
is_type=f(obj,'g_type_check_instance_is_a',[ptr,C.c_size_t],C.c_int)
item_id=f(lib,'garcon_menu_item_get_desktop_id',[ptr],C.c_char_p)
f(lib,'garcon_set_environment',[C.c_char_p],None)(b'XFCE')
class GList(C.Structure):pass
GList._fields_=[('data',ptr),('next',C.POINTER(GList)),('prev',C.POINTER(GList))]
icons={};theme=Gtk.IconTheme.get_default()
def text(value):return value.decode() if value else ''
def save_icon(value):
 if not value:return None
 if value in icons:return icons[value]
 try:
  info=theme.lookup_icon(value,64,Gtk.IconLookupFlags.FORCE_SIZE)
  if info:pix=info.load_icon()
  elif Path(value).is_file():pix=GdkPixbuf.Pixbuf.new_from_file_at_scale(value,64,64,True)
  else:pix=theme.load_icon('image-missing',64,0)
  filename=f'assets/icons/{len(icons):03d}.png';pix.savev(str(P/filename),'png',[],[])
  icons[value]=filename;return filename
 except Exception:return None

def walk(menu,depth=0):
 if depth>10:return []
 head=get_elements(menu);node=C.cast(head,C.POINTER(GList));result=[]
 while node:
  element=node.contents.data;node=node.contents.next
  if not visible(element):continue
  if is_type(element,separator_type):result.append({'separator':True});continue
  entry={'name':text(name(element)),'icon':save_icon(text(icon(element)))}
  if is_type(element,menu_type):
   entry['children']=walk(element,depth+1)
   if not entry['children']:continue
  elif is_type(element,item_type):entry['id']=text(item_id(element))
  result.append(entry)
 f(glib,'g_list_free',[ptr],None)(head)
 return result
menu=new();assert menu and load(menu,None,None)
entries=walk(menu)
extras={key:save_icon(value) for key,value in {
 'applications':'org.xfce.panel.applicationsmenu','terminal':'org.xfce.terminal','browser':'/snap/chromium/current/chromium.png',
 'files':'org.xfce.filemanager','battery':'battery-full-charged-symbolic','network':'nm-device-wired',
 'volume':'audio-volume-high','settings':'preferences-system','trash':'user-trash',
 'disk':'drive-harddisk','install':'ubiquity','text':'accessories-text-editor',
 'wifi':'network-wireless','power':'system-shutdown','folder':'folder','home':'user-home',
 'bluetooth':'bluetooth','search':'system-search'}.items()}
shutil.copy2(P/extras['applications'],P/'assets/application.png')
shutil.copy2('/usr/share/backgrounds/xfce/xfce-blue.jpg',P/'assets/wallpaper.jpg')
licenses=P/'assets/licenses';licenses.mkdir()
for style,query in [('regular','Sans'),('bold','Sans:style=Bold'),('mono','monospace')]:
 path=Path(subprocess.check_output(['fc-match','-f','%{file}',query],text=True))
 shutil.copy2(path,P/f'assets/{style}.ttf')
for package in ['fonts-noto-core','fonts-dejavu-core','xfdesktop4-data','xfce4-panel','xfce4-terminal','network-manager-gnome','chromium-browser','elementary-xfce-icon-theme','adwaita-icon-theme']:
 path=Path('/usr/share/doc')/package/'copyright'
 if path.exists():shutil.copy2(path,licenses/(package+'.copyright'))
for license_name in ['GPL-2','GPL-3','LGPL-2.1']:
 shutil.copy2(Path('/usr/share/common-licenses')/license_name,licenses/license_name)
def config(channel):return subprocess.check_output(['xfconf-query','-c',channel,'-lv'],text=True)
metadata={'capturedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reference':'CodiServer-fleet-dev-ready-20261020-amd64.iso','resolution':[1920,1080],'panelHeight':34,'iconSize':20,'workspaceCount':3,'workspaceWidth':60,'titleHeight':86,'frameBorderBottom':12,'controlWidth':66,'menuRowHeight':27,'menuFontSize':13.3333,'titleFontSize':17.3333,'font':'Noto Sans','menu':entries,'icons':extras,'settings':{c:config(c) for c in ['xfce4-panel','xfwm4','xsettings']}}
(P/'reference.json').write_text(json.dumps(metadata,indent=2)+'\n')
(P/'reference.js').write_text('window.CODI_REFERENCE = '+json.dumps(metadata,indent=2)+';\n')
with tarfile.open('/tmp/codiserver-preview-reference.tar.gz','w:gz') as archive:
 for path in P.iterdir():archive.add(path,arcname=path.name)
print('Captured real Garcon menu:',len(entries),'top-level entries;',len(icons),'icons')
