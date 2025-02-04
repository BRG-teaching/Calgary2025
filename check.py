import compas
import compas_model
import compas_notebook
import compas_occ
import compas_viewer


def check_version(package, version):
    return f"{version} => {package.__version__}  {'OK' if package.__version__ == version else 'ERROR'}"


print(f"compas          : {check_version(compas, '2.8.1')}")
print(f"compas_model    : {check_version(compas_model, '0.4.5')}")
print(f"compas_notebook : {check_version(compas_notebook, '0.8.1')}")
print(f"compas_occ      : {check_version(compas_occ, '1.2.1')}")
print(f"compas_viewer   : {check_version(compas_viewer, '1.3.0')}")
