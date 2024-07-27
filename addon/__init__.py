bl_info = {
    "name": "Processamento Grafico",
    "author": "Italo Lima",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Select Mesh > Right Click > Processamento Grafico",
    "description": "Renderiza as meshs selecionadas no renderizador passado no path",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
from . addon import *

def register():
    bpy.utils.register_class(MESH_OT_export_pg)
    bpy.utils.register_class(VIEW_PT_export_pg)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.append(draw_right_click)
    bpy.types.Scene.export_pg_path_code = bpy.props.StringProperty(
        name="Path to Code",
        description="Diretório onde o código e o executável estão localizados",
        default="",
        subtype='DIR_PATH'
    )


def unregister():
    bpy.utils.unregister_class(MESH_OT_export_pg)
    bpy.utils.unregister_class(VIEW_PT_export_pg)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_right_click)
    del bpy.types.Scene.export_pg_path_code

if __name__ == "__main__":
    register()