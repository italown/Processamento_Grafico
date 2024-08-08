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

import bpy # type: ignore
import os
import tempfile
import subprocess
import sys
import importlib
import glob

def ensure_package(package):
    try:
        # Tenta importar o pacote
        importlib.import_module(package)
        print(f"{package} já está instalado.")
    except ImportError:
        # Se falhar, instala o pacote
        print(f"{package} não encontrado. Instalando...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"{package} instalado com sucesso.")

# Verifica e instala Pillow se necessário
ensure_package('pillow')

from PIL import Image

def export_to_pg(context, path_code):
    temp_dir = tempfile.gettempdir()
    
    filepath = os.path.join(temp_dir, 'exported_selection.obj')

    selected_objects = bpy.context.selected_objects
    original_meshes = {}

    if selected_objects:
        for obj in selected_objects:
            if obj.type == "MESH":
                # Salva uma cópia da malha original
                original_meshes[obj.name] = obj.data.copy()

                # Define o objeto ativo e entra no modo de edição
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')

                # Seleciona todos os polígonos
                bpy.ops.mesh.select_all(action='SELECT')

                # Converte quadrados em triângulos
                bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

                # Retorna ao modo de objeto
                bpy.ops.object.mode_set(mode='OBJECT')
                print("Objeto convertido")

        # Exporta a seleção para OBJ
        bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True)
        print(f"Export successful: {filepath}")

        # Restaura a malha original
        for obj in selected_objects:
            if obj.type == "MESH" and obj.name in original_meshes:
                obj.data = original_meshes[obj.name]
                original_meshes[obj.name].update()
    else:
        print("No objects selected to export.")
    
    # Caminho do código C++ e do executável
    #path_code = 'C:\\Users\\italo\\Documents\\Faculdade\\Quarto Periodo\\PG\\Processamento_Grafico'
    path_code = bpy.path.abspath(path_code)
    cpp_file = os.path.join(path_code, "main.cpp")
    exe_file = os.path.join(path_code, "a.exe")
    
    # Compila o código
    compile_command = ["g++", cpp_file, "-O3", "-o", exe_file]
    compile_result = subprocess.run(compile_command, capture_output=True, text=True)
    if compile_result.returncode != 0:
        print("Compilation failed.")
        print(compile_result.stderr)
        return
    print("Compilation successful.")
    print(compile_result.stdout)
    print(compile_result.stderr)

    # Gera a imagem
    img_out = os.path.join(path_code, "image.ppm")
    run_command = f'.\\a.exe "{filepath}" > "{img_out}"'
    run_result = subprocess.run(run_command, shell=True, capture_output=True, text=True, cwd=path_code)

    if run_result.returncode != 0:
        print("Execution failed.")
        print(run_result.stderr)
        return
    print(f"Image generated: {img_out}")
    print(run_result.stdout)
    print(run_result.stderr)

    bpy.context.window_manager.popup_menu(draw_finished, title="Processamento", icon='INFO')
#    path_png = convert_ppm_to_png(img_out)
#    
#    imagem = Image.open(path_png)
#    
#    imagem.show()

def draw_finished(self, context):
    self.layout.label(text="Processamento finalizado")

def convert_ppm_to_png(path):
    im = Image.open(path)
    filepath2=path[:-4]
    filepath2= ''.join(ch for ch in filepath2)
    filepath2= filepath2+".png"
    
    im.save(filepath2)
    
    return filepath2

class MESH_OT_export_pg(bpy.types.Operator):
    """Exporta e renderiza o objeto selecionado no renderizador do Blender, além de pegar a posição da câmera"""
    bl_idname = "object.export_pg"
    bl_label = "Processamento Gráfico"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):
        path_code = context.scene.export_pg_path_code
        export_to_pg(context, path_code)
        return {'FINISHED'}

class VIEW_PT_export_pg(bpy.types.Panel):
    """Exporta para o renderizador 3D"""
    bl_label = "Exporta PG"
    bl_idname = "VIEW_PT_export_pg"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Export"
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(context.scene, "export_pg_path_code")
        box.operator("object.export_pg", icon='EXPORT')
        row = layout.row()
        row.label(text='v1.0.0', icon='INFO')
        
def draw_right_click(self, context):
    layout = self.layout
    layout.separator()
    layout.operator('object.export_pg', icon='EXPORT')
    

def menu_func(self, context):
    self.layout.operator(MESH_OT_export_pg.bl_idname, text=MESH_OT_export_pg.bl_label)


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