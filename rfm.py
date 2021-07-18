import pandas as pd
import numpy as np
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 50)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
df_=pd.read_excel("online_retail_II.xlsx" , sheet_name= "Year 2010-2011")
df=df_.copy()
df.head()

#2. Veri setinin betimsel istatistiklerini inceleyiniz.
df.describe().T

#3. Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
df.isnull().sum()


#4. Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
df.dropna(inplace=True)
df.isnull().sum()

#5. Eşsiz ürün sayısı kaçtır?

df.nunique()

#6. Hangi üründen kaçar tane vardır?
df.value_counts()

#7. En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.
df["StockCode"].value_counts().head(5)
df.groupby("StockCode").agg({"Quantity":"sum"}).sort_values(by="Quantity", ascending=False).head(5)

#8. Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
df=df[~df["Invoice"].str.contains("C", na=False)]
df

#9. Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
df["TotalPrice"] = df["Quantity"] * df["Price"]

#RFM metriklerinin hesaplanması

#Recency:Müşterinin son alışverişinden bugüne kadar geçen zaman
#Frequency:Müşterinin alışveriş sıklığı olarak tanımlanabilir.
#Monetary:Müşterinin ne kadar harcama yaptığıdır.

today_date=dt.datetime(2011,12,11)


rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.head()

rfm.columns = ["recency", "frequency", "monetary"]

rfm.describe().T

rfm = rfm[rfm["monetary"]>0]

#RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

#RFM skorlarının segment olarak tanımlanması

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

###################YORUMLAR######################
##At_Risk##
#Risk altındaki müşteriler, sık satın alma yapan büyük miktarda para harcayan ama kısa zaman önce satın almamış müşteriler.
#En son 153 gün önce satın alma işlemi yapmışlardır.
#Grupta 593 kişi vardır.
#Satın alma sıklığı 2.87 çıkmıştır.
#At risk grubunda satın alma boyutu ortalama 1084.53 sterlindir.
#Bu grubu kaybetmemek için özel kampanyalar fırsatlar veya promosyonlar önerilebilir.

##Cant_loose##
#Kaybedemez grubundaki müşteriler sık satın alma yapan ve büyük paralar harcayan  ama kısa zaman önce alışveriş yapmamışlardır.
#En son 132 gün önce alışveriş yapmışlardır.
#Grupta 63 kişi vardı.
#Alışveriş sıklık değeri 8.38 çıkmıştır.
#Cant_loose grubundaki satın alma boyutu 2796.15 sterlindir.
#Bu grup çok sık alışveriş yapan ama kısa zaman önce alışveriş yapmayanlardır.Bu kişileri kaybetmemiz şirket açısından çok büyük zarar olur.
#Önlem alınması gerekmektedir.
#Bu grup için özel teklifler ve kampanyalar düzenlenmesi gerekmektedir.

##Need_Attention##
#Dikkat gerekli olan gruptur.
#Bu grupta 187 kişi vardır.
#Bu grubun parasal boyutu 897.62 sterlindir.
#Grubun alışveriş sıklığı 2.32 çıkmıştır.
#Bu grubun en son 52 gün önce alışveriş yapması ve bu grubun kaybebedilmesi gerekmektedir.
#Bu grup için özel teklifler ve özel indirimler yaratılıp tekrar kazanılması için görüşmeler yapılmalıdır.


#"Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.

new_df = pd.DataFrame()
new_df["Loyal_Customers_ID"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.head(50)

new_df.to_excel("Loyal_Customers.xlsx")




