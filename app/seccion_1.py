from flask import Blueprint, render_template, request, send_file, url_for
import os, json, csv
import matlab.engine
import pandas as pd
import numpy as np

# Crear el blueprint
blueprint = Blueprint('seccion_1', __name__)

# Iniciar el motor de MATLAB
eng = matlab.engine.start_matlab()

# Rutas base
dir_actual = os.path.dirname(os.path.abspath(__file__))
dir_matlab = os.path.join(os.path.dirname(dir_actual), 'matlab')
dir_tables = os.path.join(dir_actual, 'tables')

# Añadir el directorio MATLAB al path
if os.path.exists(dir_matlab):
    eng.addpath(dir_matlab)
    print(f"Ruta añadida correctamente: {dir_matlab}")
else:
    print(f"La ruta de MATLAB no existe: {dir_matlab}")

eng.addpath(dir_matlab)

# Método del punto fijo
@blueprint.route('/punto_fijo', methods=['GET', 'POST'])
def punto_fijo():
    if request.method == 'POST':
        try:
            # Validar y procesar los datos del formulario
            f = str(request.form['f'])
            g = str(request.form['g'])
            x = float(request.form['x'].replace(',', '.'))
            tol = float(request.form['tol'].replace(',', '.'))
            niter = int(request.form['niter'])
            tipe = str(request.form['tipe'])

            try:
                # Intentar ejecutar MATLAB
                [r, N, xn, fm, E] = eng.pf(f, g, x, tol, niter, tipe, nargout=5)
                N, xn, fm, E = list(N[0]), list(xn[0]), list(fm[0]), list(E[0])
                length = len(N)

                # Leer la tabla generada por MATLAB
                df = pd.read_csv(os.path.join(dir_tables, 'tabla_pf.csv'))
                df = df.astype(str)
                data = df.to_dict(orient='records')
                df.to_excel(os.path.join(dir_tables, 'tabla_pf.xlsx'), index=False)

                imagen_path = os.path.join('static', 'grafica_pf.png')
                return render_template(
                    'Seccion_1/resultado_pf.html',
                    r=r, N=N, xn=xn, fm=fm, E=E,
                    length=length, data=data,
                    imagen_path=imagen_path, f=f
                )
            except matlab.engine.MatlabExecutionError as matlab_error:
                # Capturar errores específicos de MATLAB
                return render_template(
                    'Seccion_1/formulario_pf.html',
                    error_message=f"Error en MATLAB: {str(matlab_error)}"
                )

        except ValueError:
            return render_template(
                error_message="Error en los datos ingresados. Por favor verifica los valores."
            )
        except Exception as e:
            return render_template(
                'Seccion_1/formulario_pf.html',
                error_message=f"Error en la sintaxis, para mas informacion ir al apartado de ayuda"
            )

    # Si es una solicitud GET, renderiza el formulario vacío
    return render_template('Seccion_1/formulario_pf.html')


@blueprint.route('/pf/descargar', methods=['POST'])
def descargar_archivo_pf():
    archivo_path = os.path.join(dir_tables, 'tabla_pf.xlsx')
    return send_file(archivo_path, as_attachment=True)

# Ruta para el método de bisección
@blueprint.route('/biseccion', methods=['GET', 'POST'])
def biseccion():
    if request.method == 'POST':
        try:
            # Validar y procesar los datos del formulario
            f = str(request.form['f'])
            xi = float(request.form['xi'].replace(',', '.'))
            xs = float(request.form['xs'].replace(',', '.'))
            tol = float(request.form['tol'].replace(',', '.'))
            niter = int(request.form['niter'])
            tipe = str(request.form['tipe'])

            try:
                # Ejecutar la función de MATLAB
                [r, N, xn, fm, E] = eng.biseccion(f, xi, xs, tol, niter, tipe, nargout=5)

                # Convertir resultados en listas
                if len(N) != 0:
                    N, xn, fm, E = list(N[0]), list(xn[0]), list(fm[0]), list(E[0])
                else:
                    N, xn, fm, E = [], [], [], []

                length = len(N)

                # Leer y procesar la tabla de resultados
                tabla_path = os.path.join(dir_tables, 'tabla_biseccion.csv')
                if os.path.exists(tabla_path):
                    df = pd.read_csv(tabla_path)
                    df = df.astype(str)
                    data = df.to_dict(orient='records')
                else:
                    data = []

                # Procesar la ruta de la gráfica
                imagen_path = os.path.join(dir_actual, 'static', 'grafica_biseccion.png')
                if not os.path.exists(imagen_path):
                    imagen_path = None
                else:
                    imagen_path = url_for('static', filename='grafica_biseccion.png')

                # Renderizar resultados
                return render_template(
                    'Seccion_1/resultado_biseccion.html',
                    r=r, N=N, xn=xn, fm=fm, E=E,
                    length=length, data=data,
                    imagen_path=imagen_path, f=f
                )

            except matlab.engine.MatlabExecutionError as matlab_error:
                # Capturar errores específicos de MATLAB
                return render_template(
                    'Seccion_1/formulario_biseccion.html',
                    error_message=f"Error en MATLAB: {str(matlab_error)}"
                )

        except ValueError:
            return render_template(
                'Seccion_1/formulario_biseccion.html',
                error_message="Error en los datos ingresados. Por favor verifica los valores."
            )
        except Exception as e:
            return render_template(
                'Seccion_1/formulario_biseccion.html',
                error_message="Error en la sintaxis, para más información revisa el apartado de ayuda."
            )

    # Renderizar formulario vacío en GET
    return render_template('Seccion_1/formulario_biseccion.html')

# Ruta para descargar el archivo de resultados
@blueprint.route('/biseccion/descargar', methods=['POST'])
def descargar_archivo_biseccion():
    archivo_path = os.path.join(dir_tables, 'tabla_biseccion.xlsx')
    if os.path.exists(archivo_path):
        return send_file(archivo_path, as_attachment=True)
    else:
        return "Archivo no encontrado", 404


#Método de raíces múltiples
@blueprint.route('/multiple_roots', methods=['GET', 'POST'])
def multiple_roots():
    if request.method == 'POST':
        try:
            # Validar y procesar los datos del formulario
            fn = str(request.form['fn'])
            xi = float(request.form['xi'].replace(',', '.'))
            tol = float(request.form['tol'].replace(',', '.'))
            k = int(request.form['k'])
            et = str(request.form['et'])

            try:
                # Llamar a MATLAB
                [xi, errores, resultado] = eng.raices_multiples(fn, xi, tol, k, et, nargout=3)

                # Leer resultados del archivo CSV
                df = pd.read_csv(os.path.join(dir_tables, 'multiple_roots_results.csv'))
                df = df.astype(str)
                data = df.to_dict(orient='records')
                df.to_excel(os.path.join(dir_tables, 'multiple_roots_results.xlsx'), index=False)

                imagen_path = os.path.join('static', 'grafica_multiple_roots.png')

                return render_template(
                    'Seccion_1/resultado_raicesm.html',
                    data=data, imagen_path=imagen_path, resultado=resultado, fn=fn
                )

            except matlab.engine.MatlabExecutionError as matlab_error:
                # Capturar errores específicos de MATLAB
                return render_template(
                    'Seccion_1/formulario_raicesm.html',
                    error_message=f"Error en MATLAB: {str(matlab_error)}"
                )

        except ValueError:
            return render_template(
                'Seccion_1/formulario_raicesm.html',
                error_message="Error en los datos ingresados. Por favor verifica los valores."
            )
        except Exception as e:
            return render_template(
                'Seccion_1/formulario_raicesm.html',
                error_message="Error en la sintaxis, para más información revisa el apartado de ayuda."
            )

    # Renderizar formulario vacío en GET
    return render_template('Seccion_1/formulario_raicesm.html')


@blueprint.route('/rm/descargar', methods=['POST'])
def descargar_archivo_raicesm():
    archivo_path = os.path.join(dir_tables, 'multiple_roots_results.xlsx')
    return send_file(archivo_path, as_attachment=True)


#Método de la secante
@blueprint.route('/secante', methods=['GET', 'POST'])
def secante():
    if request.method == 'POST':
        try:
            # Validar y procesar los datos del formulario
            f = str(request.form['f'])
            x0 = float(request.form['x0'].replace(',', '.'))
            x1 = float(request.form['x1'].replace(',', '.'))
            tol = float(request.form['tol'].replace(',', '.'))
            Terror = str(request.form['Terror'])
            niter = int(request.form['niter'])

            try:
                # Llamar a la función de MATLAB
                respuesta = eng.secante(f, x0, x1, tol, niter, Terror)

                # Leer el archivo CSV exportado
                csv_path = os.path.join(dir_tables, 'tabla_secante.csv')
                df = pd.read_csv(csv_path)

                # Convertir a lista de diccionarios
                data = df.to_dict(orient='records')

                # Guardar el archivo Excel (opcional)
                excel_path = os.path.join(dir_tables, 'tabla_secante.xlsx')
                df.to_excel(excel_path, index=False)

                # Ruta de la gráfica
                imagen_path = os.path.join('static', 'grafica_secante.png')

                return render_template(
                    'Seccion_1/resultado_secante.html',
                    respuesta=respuesta,
                    data=data,
                    imagen_path=imagen_path,
                    f=f
                )

            except matlab.engine.MatlabExecutionError as matlab_error:
                # Capturar errores específicos de MATLAB
                return render_template(
                    'Seccion_1/formulario_secante.html',
                    error_message=f"Error en MATLAB: {str(matlab_error)}"
                )

        except ValueError:
            return render_template(
                'Seccion_1/formulario_secante.html',
                error_message="Error en los datos ingresados. Por favor verifica los valores."
            )
        except Exception as e:
            return render_template(
                'Seccion_1/formulario_secante.html',
                error_message="Error en la sintaxis, para más información revisa el apartado de ayuda."
            )

    # Renderizar formulario vacío en GET
    return render_template('Seccion_1/formulario_secante.html')


@blueprint.route('/secante/descargar', methods=['POST'])
def descargar_archivo():
    # Ruta del archivo que se va a descargar
    archivo_path = 'tables/tabla_secante.xlsx'

    # Enviar el archivo al cliente para descargar
    return send_file(archivo_path, as_attachment=True)


#Método de regla falsa
@blueprint.route('/rf', methods=['GET', 'POST'])
def reglaFalsa():
    if request.method == 'POST':
        try:
            # Validar y procesar los datos del formulario
            f = str(request.form['f'])
            x0 = float(request.form['x0'].replace(',', '.'))
            x1 = float(request.form['x1'].replace(',', '.'))
            tol = float(request.form['tol'].replace(',', '.'))
            Terror = str(request.form['Terror'])
            niter = int(request.form['niter'])

            try:
                # Llamar a la función de MATLAB
                respuesta = eng.rf(f, x0, x1, tol, niter, Terror)

                # Leer el archivo CSV exportado
                csv_path = os.path.join(dir_tables, 'tabla_reglaFalsa.csv')
                df = pd.read_csv(csv_path)

                # Convertir a lista de diccionarios
                data = df.to_dict(orient='records')

                # Guardar el archivo Excel (opcional)
                excel_path = os.path.join(dir_tables, 'tabla_reglaFalsa.xlsx')
                df.to_excel(excel_path, index=False)

                # Ruta de la gráfica
                imagen_path = os.path.join('static', 'grafica_reglaFalsa.png')

                return render_template(
                    'Seccion_1/resultado_reglaFalsa.html',
                    respuesta=respuesta,
                    data=data,
                    imagen_path=imagen_path,
                    f=f
                )

            except matlab.engine.MatlabExecutionError as matlab_error:
                # Capturar errores específicos de MATLAB
                return render_template(
                    'Seccion_1/formulario_reglaFalsa.html',
                    error_message=f"Error en MATLAB: {str(matlab_error)}"
                )

        except ValueError:
            return render_template(
                'Seccion_1/formulario_reglaFalsa.html',
                error_message="Error en los datos ingresados. Por favor verifica los valores."
            )
        except Exception as e:
            return render_template(
                'Seccion_1/formulario_reglaFalsa.html',
                error_message="Error en la sintaxis, para más información revisa el apartado de ayuda."
            )

    # Renderizar formulario vacío en GET
    return render_template('Seccion_1/formulario_reglaFalsa.html')

@blueprint.route('/rf/descargar', methods=['POST'])
def descargar_archivorf():
    # Ruta del archivo que se va a descargar
    archivo_path = 'tables/tabla_reglaFalsa.xlsx'

    # Enviar el archivo al cliente para descargar
    return send_file(archivo_path, as_attachment=True)

#Método de newton
@blueprint.route('/newton', methods=['GET', 'POST'])
@blueprint.route('/newton', methods=['GET', 'POST'])
def newton():
    if request.method == 'POST':
        try:
            # Validar y procesar los datos del formulario
            f = str(request.form['f'])
            x = float(request.form['x'].replace(',', '.'))
            tol = float(request.form['tol'].replace(',', '.'))
            niter = int(request.form['niter'])
            et = str(request.form['et'])

            try:
                # Llamar a la función de MATLAB
                [r, N, xn, fm, dfm, E, c] = eng.newton(f, x, tol, niter, et, nargout=7)

                # Leer archivo CSV
                csv_path = os.path.join(dir_tables, 'tabla_newton.csv')
                df = pd.read_csv(csv_path)
                data = df.to_dict(orient='records')

                # Guardar archivo Excel (opcional)
                excel_path = os.path.join(dir_tables, 'tabla_newton.xlsx')
                df.to_excel(excel_path, index=False)

                # Generar URL de la gráfica
                safe_f_str = ''.join(c if c.isalnum() else '_' for c in f)
                imagen_path = url_for('static', filename=f'{safe_f_str}.svg')

                return render_template(
                    'Seccion_1/resultado_newton.html',
                    r=r, f=f, data=data,
                    imagen_path=imagen_path
                )

            except matlab.engine.MatlabExecutionError as matlab_error:
                # Capturar errores específicos de MATLAB
                return render_template(
                    'Seccion_1/formulario_newton.html',
                    error_message=f"Error en MATLAB: {str(matlab_error)}"
                )

        except ValueError:
            # Capturar errores en los datos ingresados
            return render_template(
                'Seccion_1/formulario_newton.html',
                error_message="Error en los datos ingresados. Por favor verifica los valores."
            )
        except Exception as e:
            # Capturar errores generales
            return render_template(
                'Seccion_1/formulario_newton.html',
                error_message="Error en la sintaxis, para más información revisa el apartado de ayuda."
            )

    # Renderizar formulario vacío en GET
    return render_template('Seccion_1/formulario_newton.html')




@blueprint.route('/newton/descargar', methods=['POST'])
def descargar_archivo_newton():
    # Ruta del archivo que se va a descargar
    archivo_path = 'tables/tabla_newton.xlsx'

    # Enviar el archivo al cliente para descargar
    return send_file(archivo_path, as_attachment=True)

@blueprint.route('/biseccion/descargar_grafica_svg', methods=['POST'])
def descargar_grafica_biseccion_svg():
    # Obtener el nombre de la función desde el formulario
    f_str = request.form.get('f_str')
    print(f"Nombre de la función recibido: {f_str}")  # Para depuración

    if not f_str:
        return "Nombre de la función no proporcionado", 400

    # Generar un nombre seguro para el archivo
    safe_f_str = ''.join(c if c.isalnum() else '_' for c in f_str)
    archivo_path = os.path.join(dir_actual, 'static', f'{safe_f_str}.svg')

    # Verificar si el archivo existe y enviarlo
    if os.path.exists(archivo_path):
        return send_file(archivo_path, as_attachment=True, download_name=f'{safe_f_str}.svg')
    else:
        return "Gráfica SVG no encontrada", 404



@blueprint.route('/pf/descargar_grafica', methods=['POST'])
def descargar_grafica_pf():
    # Obtener el nombre de la función desde el formulario
    f_str = request.form.get('f_str')
    print(f"Nombre de la función recibido: {f_str}")  # Depuración

    if not f_str:
        return "Nombre de la función no proporcionado", 400

    # Generar el nombre seguro para el archivo
    safe_f_str = ''.join(c if c.isalnum() else '_' for c in f_str)
    archivo_path = os.path.join(dir_actual, 'static', f'grafica_{safe_f_str}.svg')

    # Verificar si el archivo existe y enviarlo
    if os.path.exists(archivo_path):
        return send_file(archivo_path, as_attachment=True, download_name=f'grafica_{safe_f_str}.svg')
    else:
        return "Gráfica SVG no encontrada", 404


@blueprint.route('/rm/descargar_grafica', methods=['POST'])
def descargar_grafica_raicesm():
    # Obtener el nombre de la función desde el formulario
    fn_str = request.form.get('fn')
    print(f"Nombre de la función recibido: {fn_str}")  # Para depuración

    if not fn_str:
        return "Nombre de la función no proporcionado", 400

    # Generar un nombre seguro para el archivo
    safe_fn_str = ''.join(c if c.isalnum() else '_' for c in fn_str)
    archivo_path = os.path.join(dir_actual, 'static', f'{safe_fn_str}.svg')

    # Verificar si el archivo existe y enviarlo
    if os.path.exists(archivo_path):
        return send_file(archivo_path, as_attachment=True, download_name=f'{safe_fn_str}.svg')
    else:
        return "Gráfica SVG no encontrada", 404
    

@blueprint.route('/rf/descargar_grafica', methods=['POST'])
def descargar_grafica_regla_falsa():
    # Obtener el nombre de la función desde el formulario
    f_str = request.form.get('f')
    if not f_str:
        return "Nombre de la función no proporcionado", 400

    # Generar un nombre seguro para el archivo
    safe_f_str = ''.join(c if c.isalnum() else '_' for c in f_str)
    archivo_path = os.path.join(dir_actual, 'static', f'{safe_f_str}.svg')

    # Verificar si el archivo existe y enviarlo
    if os.path.exists(archivo_path):
        return send_file(archivo_path, as_attachment=True, download_name=f'{safe_f_str}.svg')
    else:
        return "Gráfica SVG no encontrada", 404

@blueprint.route('/secante/descargar_grafica', methods=['POST'])
def descargar_grafica_secante():
    # Obtener el nombre de la función desde el formulario
    func_str = request.form.get('f')
    if not func_str:
        return "Nombre de la función no proporcionado", 400

    # Generar un nombre seguro para el archivo
    safe_func_str = ''.join(c if c.isalnum() else '_' for c in func_str)
    archivo_path = os.path.join(dir_actual, 'static', f'{safe_func_str}.svg')

    # Verificar si el archivo existe y enviarlo
    if os.path.exists(archivo_path):
        return send_file(archivo_path, as_attachment=True, download_name=f'{safe_func_str}.svg')
    else:
        return "Gráfica SVG no encontrada", 404


@blueprint.route('/newton/descargar_grafica', methods=['POST'])
def descargar_grafica_newton():
    # Obtener el nombre de la función desde el formulario
    f_str = request.form.get('f')
    if not f_str:
        return "Nombre de la función no proporcionado", 400

    # Generar un nombre seguro para el archivo
    safe_f_str = ''.join(c if c.isalnum() else '_' for c in f_str)
    archivo_path = os.path.join(dir_actual, 'static', f'{safe_f_str}.svg')

    # Verificar si el archivo existe y enviarlo
    if os.path.exists(archivo_path):
        return send_file(archivo_path, as_attachment=True, download_name=f'{safe_f_str}.svg')
    else:
        return "Gráfica SVG no encontrada", 404
