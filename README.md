# product-analyst-A-B-test-project-
проект по A/B тесту и статистике 
EDA пользователей
users.info()
<class 'pandas.DataFrame'>
RangeIndex: 1504 entries, 0 to 1503
Data columns (total 5 columns):
 #   Column       Non-Null Count  Dtype
---  ------       --------------  -----
 0   user_id      1504 non-null   int64
 1   group        1503 non-null   str  
 2   age          1504 non-null   int64
 3   city         1503 non-null   str  
 4   device_type  1504 non-null   str  
dtypes: int64(2), str(3)
memory usage: 58.9 KB 

Кол-во пропусков 


Распределение групп ( видно что разделение практически 50/50) группы равные








Анализ возраста 


Проверка платежей 
<class 'pandas.DataFrame'>
RangeIndex: 2661 entries, 0 to 2660
Data columns (total 7 columns):
 #   Column           Non-Null Count  Dtype         
---  ------           --------------  -----         
 0   payment_id       2661 non-null   int64         
 1   user_id          2660 non-null   float64       
 2   group            2661 non-null   str           
 3   step1_opened     2661 non-null   datetime64[us]
 4   step2_entered    2256 non-null   datetime64[us]
 5   step3_confirmed  1719 non-null   datetime64[us]
 6   step4_success    1522 non-null   datetime64[us]
dtypes: datetime64[us](4), float64(1), int64(1), str(1)
memory usage: 145.7 KB 

Также проверяем пропуски (тут можно увидеть что пользователи выпадают на шагах, но также видно, что в одной строке нет id пользователя, что является критическим пропуском) 

payment_id            0
user_id               1
group                 0
step1_opened          0
step2_entered       405
step3_confirmed     942
step4_success      1139
dtype: int64 

Поэтому я принял решение удалить данную запись
payments = payments[payments["user_id"].notna()].copy()
payments["user_id"] = payments["user_id"].astype(int)

Следом проверка, что все платежи относятся к реальным пользователям 
payments["user_id"].isin(users["user_id"]).value_counts()

user_id
True    2660
Name: count, dtype: int64 

Корректность последовательности воронки 
print(
    ((payments["step2_entered"].notna()) &
     (payments["step1_opened"].isna())).sum()
)


print(
    ((payments["step3_confirmed"].notna()) &
     (payments["step2_entered"].isna())).sum()
)


print(
    ((payments["step4_success"].notna()) &
     (payments["step3_confirmed"].isna())).sum()
)

0
0
0 

временная последовательность корректная 

Смотрим сколько было уникальных попыток
payments["user_id"].nunique()

получаем 1501, то есть из 2661 попытки оплатить, оплат было только 1501. также стоит обратить внимание на кол-во попыток на пользователя.
count    1501.000000
mean        1.772152
std         0.901878
min         1.000000
25%         1.000000
50%         2.000000
75%         2.000000
max         4.000000
dtype: float64 
видно, что максимальное значение 4.
Для теста желательно рассматривать именно завершенные платежи пользователей. 

Создаем воронку пользователей и считаем ее

valid_users = users[users["group"].isin(["A", "B"])].copy()


payments_ab = payments[
    payments["user_id"].isin(valid_users["user_id"])
].copy()


user_funnel = payments_ab.groupby("user_id").agg(
    opened=("step1_opened", "count"),
    entered=("step2_entered", lambda x: x.notna().any()),
    confirmed=("step3_confirmed", lambda x: x.notna().any()),
    success=("step4_success", lambda x: x.notna().any())
).reset_index()


user_funnel = user_funnel.merge(
    valid_users[["user_id", "group", "age", "city", "device_type"]],
    on="user_id",
    how="left"
)


funnel = user_funnel.groupby("group").agg(
    users=("user_id", "nunique"),
    opened=("opened", "count"),
    entered=("entered", "sum"),
    confirmed=("confirmed", "sum"),
    success=("success", "sum")
)


funnel["conv_1_2"] = funnel["entered"] / funnel["opened"]
funnel["conv_2_3"] = funnel["confirmed"] / funnel["entered"]
funnel["conv_3_4"] = funnel["success"] / funnel["confirmed"]
funnel["conv_1_4"] = funnel["success"] / funnel["opened"]


print(funnel)








получается:
A = 65,70%
B = 80,40%
В - тестовая группа 

можно увидеть прирост в 22.2%. получается, что из 100 пользователей новая версия приводит к 80 оплатам, тогда как старая к 66.

Также стоит обратить внимание на конверсию по шагам:
1-2 шаг
А = 89.5%
В = 94.3%
прирост на 4.8 пункта
2-3 шаг
А = 81.7%
В = 91.1%
прирост на 9.4 пункта 
3-4 шаг
А = 90%
В = 93.6%
прирост на 3.6 пункта

Из этого можно сделать аккуратный вывод, что гипотеза с автозаполнением реквизитов пользователя дает результат, так как на последнем шаге можно увидеть прирост. 

Визуализация



 конверсия
import matplotlib.pyplot as plt


conversion = funnel["conv_1_4"] * 100


plt.figure(figsize=(7, 5))
plt.bar(conversion.index, conversion.values)


plt.title("Конверсия из открытия формы в успешную оплату")
plt.xlabel("Группа")
plt.ylabel("Конверсия, %")


for i, value in enumerate(conversion.values):
    plt.text(i, value + 1, f"{value:.1f}%", ha="center")


plt.show()





воронка целиком
import numpy as np


steps = ["Открыл", "Ввел реквизиты", "Подтвердил", "Успешно"]


A = [
    funnel.loc["A", "opened"],
    funnel.loc["A", "entered"],
    funnel.loc["A", "confirmed"],
    funnel.loc["A", "success"]
]


B = [
    funnel.loc["B", "opened"],
    funnel.loc["B", "entered"],
    funnel.loc["B", "confirmed"],
    funnel.loc["B", "success"]
]


A = np.array(A) / A[0] * 100
B = np.array(B) / B[0] * 100


plt.figure(figsize=(8, 5))


plt.plot(steps, A, marker="o", label="A")
plt.plot(steps, B, marker="o", label="B")


plt.title("Воронка оплаты ЖКХ")
plt.ylabel("Доля пользователей, %")
plt.ylim(0, 105)
plt.legend()


plt.show()



10. Статистическая проверка

сравниваем две независимые группы пользователей

обозначу: 
К0 - конверсия одинаковая
К1 - конверсия в группе В больше конверсии группы А
уровень значимости = 0.05

from scipy import stats
p_A = funnel.loc["A", "conv_1_4"]
p_B = funnel.loc["B", "conv_1_4"]


n_A = funnel.loc["A", "opened"]
n_B = funnel.loc["B", "opened"]


diff = p_B - p_A


p_pool = (
    funnel.loc["A", "success"] +
    funnel.loc["B", "success"]
) / (n_A + n_B)


se = np.sqrt(
    p_pool * (1 - p_pool) *
    (1 / n_A + 1 / n_B)
)


z = diff / se


p_value = 1 - stats.norm.cdf(z)


print("A:", p_A)
print("B:", p_B)
print("Разница:", diff)
print("Z:", z)
print("p-value:", p_value)

Результат:
A: 0.6577896138482024
B: 0.804
Разница: 0.1462103861517976
Z: 6.385945004473767
p-value: 8.517109240102627e-11 

наблюдаем разницу в конверсии 65.78 - 80.4 = 14.62 пункта. 
z = 6.39. достаточно большое значение и разницу в конверсии нельзя назвать случайной.
p-value = 8.5, учитывая установленный уровень значимости в 0.05, разница также видна
исходя из этого сразу можно отбросить вариант К0 . 
Также для наглядности можно проверить uplift = 22.2%, что для продукта является существенным приростом и очень маловероятно, что он случаен. 

Доверительный интервал

0.10195391016770736
0.19046686213588784 
0.102
0.190
доверительный интервал в 95%.

В итоге: Новая форма увеличила конверсию. Поставленная гипотеза верна
