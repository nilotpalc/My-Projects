import numpy as np
import pandas as pd

tank_cap = 4800
loss_opt = [-0.004, -0.007]

main_data = pd.DataFrame(
    columns=["Loss % Scenario", "Opening Stock", "Vessel Receipt", "ITT Receipts", "Dispatches", "% Regular Stock Loss", \
             "Regular Losses", "% ITT Loss", "ITT Losses", "Total Losses", "Closing Book Stock", "Closing Actual Stock", \
             "% Total Loss"])


# Function to estimate the book stocks at the end of each month
def clos_stk_book(op_stk_, ves_rec_, itt_rec_, del_cons_):
    return op_stk_ + ves_rec_ + itt_rec_ - del_cons_


# Function to estimate the actual closing stocks at the end of each month
def gen_loss(op_stk_, ves_rec_, gen_loss_pc_):
    return (op_stk_ + ves_rec_) * gen_loss_pc_


# Function to estimate the actual closing stocks for ITT at the end of each month
def itt_stk_act(itt_rec_, itt_loss_):
    return itt_rec_ * itt_loss_


# Running the simulation over different loss options
for a in loss_opt:
    op_stk = 1500

    n = 0

    op_stk_list = []
    ves_rec_list = []
    itt_rec_list = []
    itt_act_list = []
    del_cons_list = []
    gen_loss_pc_list = []
    gen_stk_loss_list = []
    itt_pc_loss_list = []
    itt_loss_act_list = []
    clos_stk_bk_list = []
    clos_stk_act_list = []
    total_loss_list = []
    total_loss_pc_list = []

    while n < 10000:

        op_stk_list.append(op_stk)

        # Estimating the Monthly Delivery Plan
        del_cons = np.random.normal(4400, 600)
        del_cons_list.append(del_cons)

        # Estimating the ITT Transfer Size
        itt_rec = min(tank_cap - (op_stk - del_cons), np.random.normal(3000, 300))
        itt_rec_list.append(itt_rec)

        # Estimating the ITT Loss %
        itt_loss_pc = np.random.normal(a, 0.001)
        itt_pc_loss_list.append(itt_loss_pc)

        # Estimating the General Loss %
        gen_loss_pc = np.random.normal(-0.002, 0.0001)
        gen_loss_pc_list.append(gen_loss_pc)

        if op_stk + itt_rec - del_cons <= 500:
            ves_rec = min(tank_cap - (op_stk + itt_rec - del_cons), np.random.normal(3800, 200))
        else:
            ves_rec = 0

        ves_rec_list.append(ves_rec)

        # Calculate the closing book stock at an overall level
        clos_bkstk = clos_stk_book(op_stk, ves_rec, itt_rec, del_cons)
        clos_stk_bk_list.append(clos_bkstk)

        # Calculate the regular material loss
        gen_stk_loss = gen_loss(op_stk, ves_rec, gen_loss_pc)
        gen_stk_loss_list.append(gen_stk_loss)

        # Calculate the monthly ITT loss
        itt_loss = itt_rec * itt_loss_pc
        itt_loss_act_list.append(itt_loss)

        # Calculate the closing book stock at an overall level
        clos_stk_act = clos_bkstk + gen_stk_loss + itt_loss
        clos_stk_act_list.append(clos_stk_act)

        # Calculate actual loss at a monthly level
        total_loss = gen_stk_loss + itt_loss
        total_loss_list.append(total_loss)

        # Calculate % total loss at a monthly level
        total_loss_pc = total_loss / (op_stk + ves_rec + itt_rec)
        total_loss_pc_list.append(total_loss_pc)

        op_stk = clos_stk_act

        n += 1

    dataset = pd.DataFrame(
        {"Loss % Scenario": np.repeat("Loss of " + str(a), n), "Opening Stock": op_stk_list,
         "Vessel Receipt": ves_rec_list, \
         "ITT Receipts": itt_rec_list, "Dispatches": del_cons_list, "% Regular Stock Loss": gen_loss_pc_list, \
         "Regular Losses": gen_stk_loss_list, "% ITT Loss": itt_pc_loss_list, "ITT Losses": itt_loss_act_list, \
         "Total Losses": total_loss_list, "Closing Book Stock": clos_stk_bk_list,
         "Closing Actual Stock": clos_stk_act_list, "% Total Loss": total_loss_pc_list})

    main_data = main_data.append(dataset)

print(main_data)
