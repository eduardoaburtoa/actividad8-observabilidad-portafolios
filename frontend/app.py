from pathlib import Path
import streamlit as st
from frontend.client import call,BackendError
st.set_page_config(page_title='Vértice AI | Fase II',page_icon='📊',layout='wide')
st.image(str(Path(__file__).resolve().parents[1]/'documentos/vertice_logo.png'),width=85)
st.title('Preparación de revisiones de portafolio')
st.caption('Eduardo Aburto Angulo · Banquero Patrimonial Sr. · Prototipo académico')
st.info('Mi prioridad es el beneficio neto del cliente y el respeto a su perfil. Una noticia negativa no es una orden de inversión.')
a,b,c=st.tabs(['Revisar una noticia','Escenario del cliente','Evidencias y alcance'])
with a:
    st.write('El modelo fue evaluado con noticias financieras en inglés. No valida rentabilidad de fondos mexicanos. La declaración de idioma no constituye detección automática.')
    with st.form('noticia'):
        text=st.text_area('Noticia en inglés',value='The company reported a decline in operating profit.',max_chars=4000)
        submit=st.form_submit_button('Preparar revisión')
    if submit:
        try:
            result=call('/v1/predict',{'texto':text,'idioma':'en'})
            st.metric('Probabilidad de noticia negativa',f"{result['probabilidad_negativa']:.1%}")
            if result['priorizar_revision']:
                st.warning('Priorizar revisión humana')
            else:
                st.success('Sin alerta del clasificador; no implica ausencia de riesgo')
            st.caption('Umbral fijo 0.20. Meta conjunta de recall y precisión no alcanzada. Test retrospectivo.')
            with st.expander('Respuesta de la API'):st.json(result)
        except BackendError as e:st.error(str(e))
with b:
    st.caption('150 superhéroes y villanos simulados; posiciones entre 5 y 20 millones MXN. Ningún dato corresponde a clientes reales.')
    try:
        records=call('/v1/clients')['clientes']
        choice=st.selectbox('Cliente simulado',records,format_func=lambda x:f"{x['cliente_id']} · {x['nombre']} · {x['perfil_riesgo']}")
        st.metric('Posición simulada',f"${choice['posicion_mxn']:,.0f} MXN")
        with st.form('scenario'):
            proportion=st.slider('Porcentaje hipotético a migrar',1,100,35)
            increase=st.number_input('Mejora anual supuesta en puntos porcentuales',-100.0,100.0,3.0)
            months=st.number_input('Horizonte en meses',1,120,12)
            expenses=st.number_input('Gastos adicionales anuales en puntos no incluidos en rendimiento',0.0,100.0,0.0)
            profile=st.selectbox('Perfil del destino hipotético',['Conservador','Moderado','Agresivo'])
            submit2=st.form_submit_button('Comparar escenario neto')
        if submit2:
            data=call('/v1/scenario',dict(cliente_id=choice['cliente_id'],proporcion=proportion/100,mejora_anual_pp=increase,meses=months,gastos_adicionales_anuales_pp=expenses,perfil_destino=profile))
            st.metric('Beneficio incremental supuesto',f"${data['beneficio_incremental_supuesto_mxn']:,.0f} MXN")
            st.write('Perfil compatible' if data['perfil_compatible'] else 'Perfil incompatible: no elegible para revisión de migración')
            st.caption(data['supuesto']);st.json(data)
    except BackendError as e:st.error(str(e))
with c:
    st.write('Continuidad: Actividad 4 compara modelos; Actividad 5 registra entrenamiento en MLflow; Actividad 6 evalúa SVM calibrada; Fase II integra el artefacto sin reentrenarlo.')
    st.markdown('[Modelo y evaluación original](https://github.com/eduardoaburtoa/actividad6-evaluacion-portafolios) · [Fichas oficiales BBVA](https://www.bbva.mx/personas/productos/inversion/normativa-de-fondos.html)')
    st.warning('Uso académico. La licencia del corpus es no comercial. A/B simulado; no demuestra eficacia financiera. El 1 % por compra y venta es un supuesto, no una tarifa BBVA verificada.')
    st.write('Los gastos de cada fondo deben cotejarse por serie, periodicidad y vigencia. El índice heredado tiene corte al 22 de octubre de 2026; no representa una actualización automática de todas las fichas.')
