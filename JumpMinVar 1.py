import numpy as np
import pandas as pd
from datetime import timedelta
import math
import xlsxwriter


class JumpMinVar:

    def __int__(self, Jumps, StartDate, EndDate, MarketQuote, MCIL, HorizonDate):
        '''
        Description: Store data into the class
        Variables:
            @Jumps
            @StartDate
            @EndDate
            @MarketQUote
            @MCIL
            @HorizonDate
        '''
        self.Jumps = Jumps
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.MarketQuote = MarketQuote
        self.MCIL = MCIL
        self.HorizonDate = HorizonDate

    def data_retreiver(self, file):
        '''
        Description: Retrieve data from the saved_data.csv
        Variables:
            @Jumps
            @StartDate
            @EndDate
            @MarketQUote
            @MCIL
            @HorizonDate
        '''
        data = pd.read_csv("saved_db.csv")
        self.Jumps = data["Jump Date"]
        self.StartDate = data["Start Date"]
        self.EndDate = data["End Date"]
        self.MarketQuote = data["Market Quote"]
        self.MCIL = data["MCIL"][0]
        self.HorizonDate = data['Horizon Date'][0]

    def insertion_sort(self, list):
        '''
        Description: When new date is inserted into the array, then this function will sort the list least to
                     greatest
        Variables:
            @list
            @save
        '''
        # This is function is created when Jump Date is inserted, then the array of Jump Dates will be
        # re-ordered from earliest to latest .
        for i in range(1, len(list)):
            save = list[i]
            j = i
            while j > 0 and list[j - 1] > save:
                list[j] = list[j - 1]
                j -= 1
            list[j] = save

    def remove_and_order(self, list_date):
        '''
        Description: This is function is created when Jump Date is removed, then the array of Jump Dates will be
                     re-ordered from earliest to latest
        Variables:
            @list_date
        '''
        # This is function is created when Jump Date is removed, then the array of Jump Dates will be
        # re-ordered from earliest to latest .
        for i in range(0, len(list_date) - 1):
            list_date[i] = list_date[i + 1]

    def average_func(self, market_quote, start_date, end_date, N_R):
        '''
        Description: This function will compute the average forward rate using market quote
        Variables:
            @start_date
            @end_date
            @market_quote
            @N_R
        '''

        average_value = []
        for count in range(len(market_quote)):
            delta_date = (end_date[count] - start_date[count]).days
            a_i = -1 * math.log(1 / (1 + (market_quote[count] / 100) * (delta_date / 360))) * 365
            average_value.append(a_i/delta_date)

        for i in range(N_R + 1):
            average_value.append(0)
        return average_value

    def heaviside_function(self, start_date, end_date, jump_date):
        '''
        Description: This function will compute the heaviside (short-term) part of the curve
        Variables:
            @jump_date
            @start_date
            @end_date
        '''

        if end_date > jump_date and start_date > jump_date:
            value = (end_date - jump_date).days  # (end_date - jump_date).days - (start_date - jump_date).days
        elif end_date > jump_date >= start_date:
            value = (end_date - jump_date).days
        elif end_date <= jump_date < start_date:
            value = (start_date - jump_date).days
        else:
            value = 0
        return value

    def quadractic_function(self, start_date, end_date, enddate2):
        '''
        Description: The function will compute the quadratic (long-term) part of the curve
        Variables:
            @start_date
            @end_date
            @enddate2
            @delta_x
        '''

        delta_x = (end_date - start_date).days
        if start_date <= enddate2 <= end_date:
            h_x = ((enddate2 - start_date).days ** 3) / 3
        elif enddate2 > end_date:
            h_x = (delta_x ** 3) / 3 + (delta_x ** 2) * (enddate2 - end_date).days + delta_x * (
                    enddate2 - end_date).days ** 2
        else:
            h_x = 0
        return h_x

    def H_Matrix(self, start_date, end_date, new_startdate, new_enddate, jump_date, horizon_date, q, m, N_R, N_C,
                 repeatedJumpIndex):
        '''
        Description: This function constructs H-Matrix using heaviside function, quadratic function. Initially, it will
                     compute the Heaviside part of the matrix then it will compute quadratic part. *Warning: the index
                     of each value is very fragile, thus little change can create drastic impact*
        Variables:
            @start_date
            @end_date
            @new_startdate
            @new_enddate
            @jump_date
            @horizon_date
            @q
            @N_R
            @repeatedJumpIndex
        '''

        # Builds the matrix H
        n = new_startdate.count()
        p = jump_date.count()
        shift = max(p + q - n, 0)
        num_unknown = n + shift + 1
        H = np.zeros((num_unknown, num_unknown))
        new_startdate_q = new_startdate[n - q:n]
        new_enddate_q = new_enddate[n - q:n]

        for i in range(num_unknown):
            if i <= n - 1:
                H[i][0] = 1
            elif n - 1 < i <= n + N_R - 1:
                H[i][repeatedJumpIndex[i - n]] = - 1
                H[i][repeatedJumpIndex[i - n] + 1] = 1
            else:
                H[i][0] = 0

            for j in range(1, p + 1):
                if i <= n - 1:
                    H[i][j] = self.heaviside_function(start_date[i], end_date[i], jump_date[j - 1]) / (
                        (end_date[i] - horizon_date).days)
                elif i == num_unknown - 1:
                    H[i][j] = 0

        for i in range(num_unknown):

            for j in range(q):
                H_Col = p + j + 1
                if i <= n - 1:

                    H[i][H_Col] = self.quadractic_function(new_startdate_q[j + (n - q)], new_enddate_q[j + (n - q)],
                                                           end_date[
                                                               i]) / (end_date[
                                                                          i] - horizon_date).days  # - quadractic_function(start_date[j - 1], end_date[j - 1], horizon_date))/(end_date[i] - horizon_date).days
                elif i == num_unknown - 1:
                    H[i][H_Col] = -2 * float((new_enddate_q[j + (n - q)] - new_startdate_q[j + (n - q)]).days)

        return H

    def PreProcessing(self):
        # Pre-Defined variables:
        '''
        Description: Pre-processing is one of the two main Jump MinVar algorithms, where it will decide to add a
                     virtual jump date, remove the actual jump date, modify the start date and end date depending on the conditions of the algorithm
        Variables:
            @JumpPointsArray
            @StartDateArray
            @EndDateArray
            @m = Number of jumps, initially
            @MCIL
            @HorizonDate
            @TotalNumberOfJumpPoints = this will be used separately from variable "m"
            @TotalNumberofIntervals
            @VirtualJumpDate
            @CaseLog
            @N_R
            @N_C
            @RepeatedJump
            @RepeatedJumpIndex
            @LastJumpIsRepeated
            @OutOfRange
            @ReachedEnd
            @HeavisideDates
            @i
            @j
            @same_loop

        Return: None
        '''


        JumpPointsArray = pd.to_datetime(self.Jumps)
        StartDateArray = pd.to_datetime(self.StartDate)  # a # initial end dates
        EndDateArray = pd.to_datetime(self.EndDate)  # b
        m = JumpPointsArray.count()
        MCIL = self.MCIL
        HorizonDate = self.HorizonDate
        TotalNumberOfJumpPoints = JumpPointsArray.count()  # JumpPointsArray.count()
        TotalNumberofIntervals = len(StartDateArray) - 1  # n
        VirtualJumpDate = []
        CaseLog = []
        N_R = 0
        N_C = 0
        RepeatedJump = []
        RepeatedJumpIndex = []
        LastJumpIsRepeated = False
        OutOfRange = True
        ReachedEnd = True
        HeavisideDates = []
        i = 0
        j = 0
        same_loop = False

        if JumpPointsArray.count() == 0:
            ReachedEnd = False

        while ReachedEnd:

            j = i - N_R
            LastJumpIsRepeated = False
            TotalNumberOfJumpPoints = JumpPointsArray.count()


            ############################################################################################################################
            # Following loop is normalizing every interval, such that i-th interval will be
            # compared against i+1,..., n intervals, in the end co-head/co-tail is entirely removed.
            for k in range(j, TotalNumberofIntervals):

                # If s_i = s_j or e_i = e_j, then continue:
                if StartDateArray[j] == StartDateArray[k + 1] or EndDateArray[j] == EndDateArray[k + 1]:


                    if StartDateArray[j] == StartDateArray[k + 1]:
                        # If s_i = s_j then:
                        #   If e_i < e_j then s_j = e_i
                        #   else: s_i = e_j
                        if EndDateArray[j] < EndDateArray[k + 1]:
                            StartDateArray[k + 1] = EndDateArray[j]
                        else:
                            StartDateArray[j] = EndDateArray[k + 1]
                    else:
                        # If e_i = e_j then:
                        #   If s_i < s_j then e_i = s_j
                        #   else: e_j = s_i
                        if StartDateArray[j] < StartDateArray[k + 1]:
                            EndDateArray[j] = StartDateArray[k + 1]
                        else:
                            EndDateArray[k + 1] = StartDateArray[j]
            ############################################################################################################################



            # Case1: Jump Date is greater than current end date but less than next end date, then change the current
            # end date to jump date.

            if j >= TotalNumberofIntervals:
                OutOfRange = False

            if EndDateArray[j] <= JumpPointsArray[i] and OutOfRange:

                if j < TotalNumberofIntervals and JumpPointsArray[i] + timedelta(days=MCIL) < EndDateArray[j + 1]:
                    # Case 1: Line up interval j with jump i
                    # Jump Date is greater than current end date but less than next end date, then change the current
                    # end date to jump date.

                    # This condition is to track if the iteration is coming back second time, because virtual jump
                    # was added in the previous iteration.

                    if same_loop == True:
                        CaseLog.append("Case 2/Case 1")
                        same_loop = False
                    else:
                        CaseLog.append("Case 1")

                    EndPoint = EndDateArray[j]
                    EndDateArray[j] = JumpPointsArray[i]
                    i = i + 1

                    if i == TotalNumberOfJumpPoints:  # when iteration reaches total number of jumps, then while loop stops.
                        ReachedEnd = False


                else:  # Case 2: Clean Period (one or more intervals without jump)
                    # When the jump date is greater than current and next end date. We insert virtual jump, which is equal to
                    # current end date
                    # print("case2")

                    same_loop = True  # Method to track if virtual jump is added, and it will need same loop

                    EndPoint = EndDateArray[j]
                    JumpPointsArray[JumpPointsArray.count()] = EndDateArray[j]
                    self.insertion_sort(JumpPointsArray)
                    VirtualJumpDate.append(str(EndPoint))
                    N_C = N_C + 1

                    if i == TotalNumberOfJumpPoints:
                        ReachedEnd = False

            else:  # Line up end-point of interval j with jump i

                if j < TotalNumberofIntervals and StartDateArray[j] < JumpPointsArray[i] - timedelta(days=MCIL):
                    # Case 3: Line up end-point of interval j with jump i
                    # If jump date is less than current end date but greater than start date
                    # current end date = jump date

                    CaseLog.append("Case 3")
                    # print("case3")
                    EndPoint = EndDateArray[j]
                    EndDateArray[j] = JumpPointsArray[i]
                    i = i + 1

                    if i == TotalNumberOfJumpPoints:
                        ReachedEnd = False

                else:  # Repeated Jump
                    # Case 4: If the jump date is less than both start date and end date, then it is considered repeated jump dates
                    # print("case4")
                    EndPoint = EndDateArray[j]
                    CaseLog.append("Case 4")
                    if i == 0:
                        # RepeatedJump.append(str(JumpPointsArray[i]))
                        remove_and_order(JumpPointsArray)
                        TotalNumberOfJumpPoints = JumpPointsArray.count()

                        # if TotalNumberOfJumpPoints-1 < 0: continue
                        if i == TotalNumberOfJumpPoints:
                            ReachedEnd = False

                    else:
                        N_R = N_R + 1
                        RepeatedJumpIndex.append(i)
                        RepeatedJump.append(str(JumpPointsArray[i]))

                        if i == TotalNumberOfJumpPoints - 1:
                            LastJumpIsRepeated = True

                        i = i + 1

                        if i == TotalNumberOfJumpPoints:
                            ReachedEnd = False

        # Following "if statement" condition is to check if the last jump is closer to the left of the interval or
        # right of the interval. If it is closer to the left, then end date of that interval will be new virtual jump
        # and repeated jump.

        if JumpPointsArray.count() > 0:
            ######Adding

            if TotalNumberOfJumpPoints == 0:
                print("No Qualified Jumps")
            else:
                LastJump = JumpPointsArray[JumpPointsArray.count() - 1]

            if LastJump < EndPoint and not LastJumpIsRepeated:
                Distance1 = float((LastJump - StartDateArray[TotalNumberOfJumpPoints]).days)
                Distance2 = float((EndPoint - LastJump).days)
                if Distance1 < Distance2:
                    JumpPointsArray[JumpPointsArray.count()] = EndPoint
                    N_C = N_C + 1
                    N_R = N_R + 1
                    TotalNumberOfJumpPoints = TotalNumberOfJumpPoints + 1
                    # RepeatedJumpIndex.insert(TotalNumberOfJumpPoints + 1
                    LastJump = EndPoint

                    RepeatedJumpIndex.append(i)
                    RepeatedJump.append(str(LastJump))
                    VirtualJumpDate.append(str(LastJump))

            elif EndPoint < LastJump:
                JumpPointsArray[JumpPointsArray.count() + 1] = np.NaN
                LastJump = JumpPointsArray[JumpPointsArray.count() + 1]

            # Adjust Interval Start Points for the remaining Min Var
            for k in range(j, StartDateArray.count()):
                if EndDateArray[k] > LastJump and StartDateArray[k] < LastJump:
                    StartDateArray[k] = LastJump

        # Organizes the array of heaviside dates
        HeavisideDates.append(pd.to_datetime(self.HorizonDate))
        for i in range(1, TotalNumberOfJumpPoints):
            HeavisideDates.append(JumpPointsArray[i - 1])

        #Keeping track of the repeated jump
        N_Repeated = 0
        RepeatedJump = pd.Series(RepeatedJump)
        for i in range(RepeatedJump.count()):
            if RepeatedJump[i] != "NaT":
                N_Repeated = N_Repeated + 1

        # Recording all the data internally
        self.N_R = N_Repeated
        self.RepeatedJumpIndex = RepeatedJumpIndex[0:self.N_R]
        self.N_C = N_C
        self.m = m
        self.JumpPoints = JumpPointsArray
        self.StartDateArray = StartDateArray
        self.EndDateArray = EndDateArray
        self.SplineDate(StartDateArray, EndDateArray, JumpPointsArray, self.N_R)

        #Converting data into panda series
        case_log = pd.Series(CaseLog)
        VirtualJumpDate = pd.Series(VirtualJumpDate)
        SplineEndDate = pd.Series(self.SplineEndDate)
        SplineStartDate = pd.Series(self.SplineStartDate)
        HeavisideDate = pd.Series(HeavisideDates)

        #Collecting all the data into dataframe for log file
        test_df = pd.DataFrame(
            {'Case': case_log, 'Start Date': StartDateArray, 'End Date': EndDateArray, 'Jump Points': JumpPointsArray,
             'Virtual': VirtualJumpDate, 'Repeated': RepeatedJump, 'Spline Start Date': SplineStartDate,
             'Spline End Date': SplineEndDate, 'Heaviside Date': HeavisideDate})
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)
        self.Results = test_df

    def SplineDate(self, StartDate, EndDate, Jumps, NR):
        ################Spline Dates##################

        n = len(StartDate)
        jump_len = Jumps.count()
        ind_jump = jump_len - NR

        self.SplineStartDate = StartDate[ind_jump:n]
        self.SplineEndDate = EndDate[ind_jump:n]
        self.q = n - ind_jump

    def controller(self, data):
        '''
        # This function will be the centre that will be calling all the functions and collecting computed
        # information, such as jump dates (virtual vs. repeated), normalized intervals, matrix H, average forward rate
        :param data:
        :return: final_result. lambda_vector
        '''


        self.data_retreiver(data)
        self.PreProcessing()

        # Matrix H
        H = self.H_Matrix(pd.to_datetime(self.StartDate), pd.to_datetime(self.EndDate), self.StartDateArray,
                          self.EndDateArray, self.JumpPoints, pd.to_datetime(self.HorizonDate), self.q, self.m,
                          self.N_R, self.N_C, self.RepeatedJumpIndex)
        H_df = pd.DataFrame(H)
        H_df.to_csv("H.csv", encoding='utf-8', index=False)
        print(np.linalg.cond(H))

        # Matrix Inversed H
        inv_H = np.linalg.inv(H)
        inv_H_df = pd.DataFrame(inv_H)

        # Average Forward Rate
        A = self.average_func(self.MarketQuote, pd.to_datetime(self.StartDateArray), pd.to_datetime(self.EndDateArray),
                              self.N_R)
        A_df = pd.DataFrame({'Average': A})

        # Lambda Vector
        self.lambda_vec = inv_H.dot(A)
        lambda_df = pd.DataFrame({'Lambda': self.lambda_vec})

        # Excel Log File
        self.writer = pd.ExcelWriter('log.xlsx')
        self.Results.to_excel(self.writer, 'log', startrow=0, startcol=0)
        H_df.to_excel(self.writer, 'log', startrow=0, startcol=15)
        inv_H_df.to_excel(self.writer, 'log', startrow=40, startcol=15)
        A_df.to_excel(self.writer, 'log', startrow=40, startcol=6)
        self.MarketQuote.to_excel(self.writer, 'log', startrow=40, startcol=4)
        self.StartDate.to_excel(self.writer, 'log', startrow=40, startcol=0)
        self.EndDate.to_excel(self.writer, 'log', startrow=40, startcol=2)
        lambda_df.to_excel(self.writer, 'log', startrow=40, startcol=8)

        # save the excel file
        self.writer.save()
        final_result = self.Results

        return final_result, self.lambda_vec



    def nonnull_count(self, data):
        count = 0
        for i in range(len(data)):
            if data[i] == 'NaN':
                count = count + 1
        return count

    def fwd_function(self, result, lamdba_v, date):
        # forward function:
        # Data Organization:

        '''
        Description: This function will take in the date of the curve, and compute the forward rate using
                     lambda and amended intervals.

        :param result:
        :param lamdba_v:
        :param date:
        :return: zc_rate, df
        '''

        JumpPoints_fwd = result['Jump Points']
        StartDate_fwd = result['Start Date']
        EndDate_fwd = result['End Date']
        splinedate = result['Spline Start Date']
        p = JumpPoints_fwd.count()
        n = StartDate_fwd.count()
        q = self.q
        lambda_p = lamdba_v[0:p + 1]
        lambda_q = lamdba_v[p:p + q]
        startdate_p = StartDate_fwd[0:p]
        startdate_q = StartDate_fwd[n - q:n]
        enddate_p = EndDate_fwd[0:p]
        enddate_q = EndDate_fwd[n - q:n]


        '''
            for k in range(n-q,n-1):
            if startdate_q[k] == startdate_q[k+1]:
                for j in range(k,n):
                    startdate_q[j] = enddate_q[k]
        '''

        #########################################################

        date = pd.to_datetime(date)
        func_H = []

        #Piecewise H(x)
        for row_count in range(p+1):
            if date >= self.JumpPoints[row_count]:
                func_H.append(1)
            else:
                func_H.append(0)

        #Quadratic Function Q(x)
        func_q = []
        for row_count in range(n - q, n):
            if date < startdate_q[row_count]:
                func_q.append(0)
            elif startdate_q[row_count] <= date < enddate_q[row_count]:
                func_q.append(((date - startdate_q[row_count]).days**2)/360)
            else:
                x_delta = (enddate_q[row_count] - startdate_q[row_count]).days
                func_q.append((x_delta ** 2 + 2 * x_delta * (date - enddate_q[row_count]).days)/365)

        func_H = np.asarray(func_H, dtype=np.float32)
        func_q = np.asarray(func_q, dtype=np.float32)
        fwd_f = func_H.T.dot(lambda_p) + func_q.T.dot(lambda_q)
        return fwd_f

    def interpolation(self, data, lambda_v, date1, date2):
        fwd_rate1 = self.fwd_function(data, lambda_v, date1)
        fwd_rate2 = self.fwd_function(data, lambda_v, date2)
        print(fwd_rate1)
        print("  ")
        print(fwd_rate2)
        zc_rate = fwd_rate2#(1 + fwd_rate2) / (1 + fwd_rate1) - 1
        df = 1 / (1 + zc_rate)

        return zc_rate*100, df


'''
    def fwd_vector(self, date_list):
        given_date = pd.to_datetime(np.)
        length = len(date_list)
        fwd_list = []
        for i in range(length):
            fwd_list.append(self.fwd_function(date_list[i]))
        return np.asarray(fwd_list, dtype=np.float32)
'''
