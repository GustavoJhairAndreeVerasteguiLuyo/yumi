import sqlite3
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px

DB=Path("almuerzos_nemby.db")
st.set_page_config(page_title="Almuerzos | Ñemby",page_icon="🍽️",layout="wide")

def read(sql,params=()):
    con=sqlite3.connect(DB)
    df=pd.read_sql_query(sql,con,params=params)
    con.close()
    return df

st.title("🍽️ Planificador predictivo de almuerzos")
st.caption("Ñemby, Paraguay · Pronóstico de platos, porciones e ingredientes")
if not DB.exists():
    st.error("No se encuentra almuerzos_nemby.db. Ejecuta: sqlite3 almuerzos_nemby.db < schema.sql")
    st.stop()

dishes=read("SELECT * FROM platos WHERE activo=1 ORDER BY nombre")
ingredients=read("SELECT * FROM ingredientes WHERE activo=1 ORDER BY nombre")
sales=read("""SELECT v.fecha,v.plato_id,p.nombre plato,v.porciones_vendidas,
 v.precio_unitario,v.sobrantes,v.porciones_vendidas*v.precio_unitario facturacion
 FROM ventas_almuerzo v JOIN platos p USING(plato_id) ORDER BY v.fecha""")
if dishes.empty:
    st.warning("Agrega los platos de fondo en la tabla platos.")
    st.stop()

with st.sidebar:
    st.header("Parámetros")
    target=date.today()+timedelta(days=1)
    target_day=st.date_input("Día a planificar",target)
    reserve=st.slider("Margen de seguridad (%)",0,40,10)
    budget=st.number_input("Presupuesto de compra (₲)",min_value=0,value=500000,step=50000)

a,b,c,d=st.columns(4)
a.metric("Platos registrados",len(dishes))
b.metric("Porciones vendidas",int(sales.porciones_vendidas.sum()) if not sales.empty else 0)
c.metric("Facturación",f"₲ {sales.facturacion.sum():,.0f}" if not sales.empty else "₲ 0")
d.metric("Ingredientes",len(ingredients))

st.subheader("Pronóstico de porciones por plato")
forecast=[]
weekday=target_day.weekday()
for _,p in dishes.iterrows():
    s=sales[sales.plato_id==p.plato_id].copy()
    if s.empty:
        estimate=0
        basis="Sin historial"
    else:
        s["fecha"]=pd.to_datetime(s.fecha)
        same=s[s.fecha.dt.weekday==weekday].sort_values("fecha").tail(8)
        recent=s.sort_values("fecha").tail(28)
        same_avg=same.porciones_vendidas.mean() if len(same) else 0
        recent_avg=recent.porciones_vendidas.mean()
        estimate=round(0.7*same_avg+0.3*recent_avg)
        basis=f"{len(same)} registros del mismo día y {len(recent)} recientes"
    forecast.append({"Plato":p.nombre,"Porciones estimadas":estimate,
                     "Precio (₲)":p.precio_venta,"Venta potencial (₲)":estimate*p.precio_venta,
                     "Base del cálculo":basis})
fdf=pd.DataFrame(forecast)
st.dataframe(fdf,use_container_width=True,hide_index=True)

st.subheader("Ingredientes necesarios y orden de compra")
recipes=read("""SELECT p.nombre plato,i.ingrediente_id,i.nombre ingrediente,i.unidad,
 r.cantidad_por_porcion,i.stock_actual,i.stock_seguridad,i.costo_unitario
 FROM recetas r JOIN platos p USING(plato_id)
 JOIN ingredientes i USING(ingrediente_id)""")
if recipes.empty:
    st.info("Carga las recetas con la cantidad de cada ingrediente por porción. Luego se calculará la compra automáticamente.")
else:
    needs=[]
    for _,r in recipes.iterrows():
        portions=float(fdf.loc[fdf.Plato==r.plato,"Porciones estimadas"].iloc[0])
        required=portions*float(r.cantidad_por_porcion)*(1+reserve/100)
        buy=max(0,required+float(r.stock_seguridad)-float(r.stock_actual))
        needs.append({"Ingrediente":r.ingrediente,"Unidad":r.unidad,
          "Necesidad bruta":round(required,3),"Stock":r.stock_actual,
          "Comprar":round(buy,3),"Costo estimado (₲)":round(buy*r.costo_unitario,0)})
    ndf=pd.DataFrame(needs).groupby(["Ingrediente","Unidad"],as_index=False).agg(
        {"Necesidad bruta":"sum","Stock":"first","Comprar":"sum","Costo estimado (₲)":"sum"})
    st.dataframe(ndf,use_container_width=True,hide_index=True)
    total=ndf["Costo estimado (₲)"].sum()
    st.metric("Costo total estimado de compra",f"₲ {total:,.0f}")
    if total>budget: st.warning("La compra estimada supera el presupuesto. Ajusta porciones, platos o stock.")
    st.download_button("Descargar orden de compra CSV",ndf.to_csv(index=False).encode("utf-8-sig"),
                       "orden_compra_almuerzo.csv","text/csv")

col1,col2=st.columns(2)
with col1:
    st.subheader("Demanda histórica por plato")
    if not sales.empty:
        sales["fecha"]=pd.to_datetime(sales.fecha)
        agg=sales.groupby(["fecha","plato"],as_index=False).porciones_vendidas.sum()
        st.plotly_chart(px.line(agg,x="fecha",y="porciones_vendidas",color="plato",markers=True),use_container_width=True)
    else: st.info("Registra las ventas diarias para activar los gráficos.")
with col2:
    st.subheader("Rentabilidad estimada por plato")
    prof=dishes.copy()
    prof["margen bruto (₲)"]=prof.precio_venta-prof.costo_estimado
    st.plotly_chart(px.bar(prof,x="nombre",y="margen bruto (₲)"),use_container_width=True)

st.subheader("Registrar venta de almuerzo")
with st.form("venta"):
    x,y,z,q=st.columns(4)
    plato=x.selectbox("Plato",dishes.nombre.tolist())
    fecha=y.date_input("Fecha",date.today())
    porciones=z.number_input("Porciones vendidas",0,1000,1)
    precio=q.number_input("Precio por porción (₲)",0,1000000,0,step=500)
    sobrantes=st.number_input("Porciones sobrantes",0,1000,0)
    if st.form_submit_button("Guardar venta") and porciones>=0:
        pid=int(dishes.loc[dishes.nombre==plato,"plato_id"].iloc[0])
        con=sqlite3.connect(DB)
        con.execute("""INSERT INTO ventas_almuerzo(fecha,plato_id,porciones_vendidas,
          precio_unitario,sobrantes) VALUES(?,?,?,?,?)""",
          (fecha.isoformat(),pid,porciones,precio,sobrantes))
        con.commit();con.close()
        st.success("Venta registrada. Actualiza la página para ver el pronóstico.")

st.caption("El pronóstico necesita historial. La precisión mejora al registrar ventas, sobrantes, recetas, stock y costos diariamente.")
