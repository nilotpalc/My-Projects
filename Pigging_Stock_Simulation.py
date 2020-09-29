import random

import numpy as np
import pandas as pd

opg_stk_options = [80, 100, 120, 150]

df_consol = pd.DataFrame(
    columns=['Day Count', 'Opg_Stk', 'Cons_Qty', 'PLT Lead Time', 'On Order Qty', 'Receipt Qty', 'Supply Lead Time',
             'Cls_Stk', 'Scenario', 'Max_Order_Limit'])

for aa in opg_stk_options:

    # Simulating the Pigging Consumption, Ordering and Order Receipt days

    cons_day = 0  # Setting the start counter to zero

    z = 700  # Defining the number of PLT and associated order-receipt cycles

    """
    Setting the initial parameters
    """
    cons_day_list = []
    order_day_list = []
    order_rec_list = []

    # Simulating the PLT Consumption and Order-Receipt Cycles
    n = 0

    while n < z:
        plt_lead_time = random.randrange(5, 8, 1)
        cons_day += plt_lead_time
        if random.randrange(1, 6) == 5:
            cons_qty = 100
        else:
            cons_qty = 50
        order_day = cons_day

        order_qty = cons_qty

        if order_qty == 50:
            order_rec = order_day + random.randrange(4, 7, 1)
        else:
            order_rec = order_day + random.randrange(7, 9, 1)

        # adding integers to a list changes the type to string when used in a dataframe
        # creates a tuple (date of plt/order/receipt, qty, lead time)
        cons_day_list.append((cons_day, cons_qty, plt_lead_time))
        order_day_list.append((order_day, order_qty))
        order_rec_list.append((order_rec, order_qty, order_rec - order_day))
        n += 1

    # Generating the data frame for N2 consumption
    df_cons = pd.DataFrame(cons_day_list, columns=["Cons_Day", "Cons_Qty", "PLT Lead Time"])

    # Generating the data frame for N2 order placement
    df_ord_day = pd.DataFrame(order_day_list, columns=["Order_Day", "On Order Qty"])

    # Generating the data frame for N2 order receipts
    df_ord_rec = pd.DataFrame(order_rec_list, columns=["Order_Rec_Day", "Receipt Qty", "Supply Lead Time"])
    df_ord_rec = df_ord_rec.groupby('Order_Rec_Day').agg({'Receipt Qty': 'sum', "Supply Lead Time": 'max'})
    df_ord_rec.reset_index(inplace=True)

    """
    Combining multiple dataframes along with opening stock dataframe
    This is to link the day counter generated using the opening stock dataframe to \
    the other dataframes
    """
    # taking max of the days in cons_dataframe to create a total list of days to simulate
    df_op_stk = pd.DataFrame({"Opg_Stk": np.repeat(aa, df_cons['Cons_Day'].max() + 1)})
    df_op_stk.reset_index(inplace=True)
    df_op_stk.rename(columns={'index': "Day Count"}, inplace=True)

    df_ops_cons = df_op_stk.merge(df_cons, left_on="Day Count", right_on="Cons_Day", how="left")
    df_ops_co_ord = df_ops_cons.merge(df_ord_day, left_on='Day Count', right_on='Order_Day', how='left')

    # Completing the final dataframe
    df_main = df_ops_co_ord.merge(df_ord_rec, left_on='Day Count', right_on='Order_Rec_Day', how='left')

    df_main.drop(['Cons_Day', 'Order_Day', 'Order_Rec_Day'], axis=1, inplace=True)

    df_main.fillna(0, inplace=True)
    df_main.set_index('Day Count', inplace=True)

    # Running a for loop to re-assign the opg_stock from the previous row except for the first row
    for i in range(len(df_main)):
        if i == 0:
            df_main.loc[i, "Opg_Stk"] = aa
        else:
            df_main.loc[i, "Opg_Stk"] = df_main.loc[i - 1, "Opg_Stk"] + df_main.loc[i - 1, "Receipt Qty"] - df_main.loc[
                i - 1, "Cons_Qty"]

    df_main['Cls_Stk'] = df_main['Opg_Stk'] + df_main['Receipt Qty'] - df_main['Cons_Qty']
    df_main = df_main.assign(Scenario=lambda x: "Opg Stk of " + str(aa))
    df_main = df_main.assign(Max_Order_Limit=lambda x: aa)
    df_consol = pd.concat([df_consol, df_main.reset_index()], ignore_index=True, join='inner')

df_consol.set_index('Day Count', inplace=True)
print(df_consol)
