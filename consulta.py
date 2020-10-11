import mysql.connector
from time import time

# import datetime

print(mysql.connector.__version__)

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='mautic'
)

print(db)

cursor = db.cursor(buffered=True)


def return_email_readers():
    cursor.execute(
        """
        SELECT distinct
            lead_id
        FROM
            email_stats 
        WHERE
            is_read = 1 
            and lead_id is not null
        LIMIT 100;
            
        """
    )
    return cursor.fetchall()


def read_count_hour_by_lead_id(lid):
    inicio = time()
    cursor.execute(
        """
        SELECT if(
            time_format(es.date_read,'%H') -3 < 0, 
            24 - ((time_format(es.date_read,'%H') -3) * -1), 
            time_format(es.date_read,'%H') -3
        )
            as read_time, count(1)
        FROM
            email_stats es
        WHERE 
            es.is_read = 1
            and es.lead_id is not null 
            and es.email_id is not null 
            and es.lead_id = {lid}
        GROUP BY
            read_time 
        ORDER BY
            2 desc;
        """.format(lid=lid))
    print('Tempo: ', time() - inicio, ' seg.')
    return cursor.fetchall()


def bubble_sort(nums):
    # Definimos swapped para True para que o loop pareça ser executado pelo menos uma vez
    swapped = True
    while swapped:
        swapped = False
        for j in range(len(nums) - 1):
            if nums[j] > nums[j + 1]:
                # Troque os elementos
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
                # Defina o sinalizador como True para que possamos fazer um loop novamente
                swapped = True


def percentage_or_score(counter_num, firstnum, score=True):
    percentage = counter_num * 100 / firstnum
    if score is True:
        scoreresult = percentage * counter_num
        return int(scoreresult)
    else:
        return int(percentage)


def best_hour(list_itens):
    h = [0, 0]
    for index, item in enumerate(list_itens):
        if h[1] < list_itens[index][1]:
            h = list_itens[index]
    return 'Hora: ', h[0], 'Pontuação: ', h[1]


def hour_summation(itens, consecutive_hours=3, hour_diff=6):
    bubble_sort(itens)
    linhas = len(itens)
    if linhas < consecutive_hours:
        return False
    itens = itens + itens[:consecutive_hours - 1]

    valid_consecutive_hours = []

    i = 1
    while i <= linhas:
        swap = itens[i - 1: (i - 1) + consecutive_hours]
        if swap[0][0] > swap[-1][0]:
            if swap[0][0] - swap[-1][0] <= hour_diff:
                valid_consecutive_hours.append(swap)
        else:
            if swap[-1][0] - swap[0][0] <= hour_diff:
                valid_consecutive_hours.append(swap)
        i += 1
    point_group = []
    i = 0
    while i < len(valid_consecutive_hours):
        j = 0
        summ = 0
        while j < consecutive_hours:
            summ += valid_consecutive_hours[i][j][1]
            j += 1

        point_group.append(
            ['{} -- {}'.format(valid_consecutive_hours[i][0][0], valid_consecutive_hours[i][-1][0]), summ]
        )
        i += 1

    i = 0
    indx_val = [0, 0]

    print('Grupos de pontos', point_group)

    while i < len(point_group):

        if indx_val[1] < point_group[i][1]:
            indx_val = point_group[i]
        i += 1

    return indx_val


for i in return_email_readers():
    print('ID: ', i[0])
    first = None
    hours_and_points = []
    print('Hora;vezes lidas;porcentagem;pontuação')
    for hour, counter in read_count_hour_by_lead_id(i[0]):
        hour = int(hour)
        if first is None:
            first = counter
        print(hour, ';', counter, ';', percentage_or_score(counter, first, False),
              ';', percentage_or_score(counter, first))
        hours_and_points.append([hour, percentage_or_score(counter, first)])
    print('Melhor grupo de horas: ', hour_summation(hours_and_points, 4, 6))
    print('Melhor hora: ', best_hour(hours_and_points))

    print('-' * 30)
