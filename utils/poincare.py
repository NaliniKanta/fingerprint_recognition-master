from utils import orientation
import math
import cv2 as cv
import numpy as np

def poincare_index_at(i, j, angles, tolerance):
    """
    compute the summation difference between the adjacent orientations such that the orientations is less then 90 degrees
    https://books.google.pl/books?id=1Wpx25D8qOwC&lpg=PA120&ots=9wRY0Rosb7&dq=poincare%20index%20fingerprint&hl=pl&pg=PA120#v=onepage&q=poincare%20index%20fingerprint&f=false
    :param i:
    :param j:
    :param angles:
    :param tolerance:
    :return:
    """
    cells = [(-1, -1), (-1, 0), (-1, 1),         # p1 p2 p3
            (0, 1),  (1, 1),  (1, 0),            # p8    p4
            (1, -1), (0, -1), (-1, -1)]          # p7 p6 p5

    angles_around_index = [math.degrees(angles[i - k][j - l]) for k, l in cells]
    index = 0
    for k in range(0, 8):

        # calculate the difference
        difference = angles_around_index[k] - angles_around_index[k + 1]
        if difference > 90:
            difference -= 180
        elif difference < -90:
            difference += 180

        index += difference

    if 180 - tolerance <= index <= 180 + tolerance:
        return "loop"
    if -180 - tolerance <= index <= -180 + tolerance:
        return "delta"
    if 360 - tolerance <= index <= 360 + tolerance:
        return "whorl"
    return "none"


def calculate_singularities(im, angles, tolerance, W, mask):
    result = cv.cvtColor(im, cv.COLOR_GRAY2RGB)

    # DELTA: RED, LOOP:ORAGNE, whorl:INK
    colors = {"loop" : (0, 0, 255), "delta" : (0, 128, 255), "whorl": (255, 153, 255)}
    my_input=[]
    delta_x=[]
    delta_y=[]
    loop_x=[]
    loop_y=[]

    for i in range(3, len(angles) - 2):             # Y
        for j in range(3, len(angles[i]) - 2):      # x
            # mask any singularity outside of the mask
            mask_slice = mask[(i-2)*W:(i+3)*W, (j-2)*W:(j+3)*W]
            mask_flag = np.sum(mask_slice)
            if mask_flag == (W*5)**2:
                singularity = poincare_index_at(i, j, angles, tolerance)
                if singularity == "delta":
                    my_input.append(singularity)
                    delta_x.append(((j+0)*W, (i+0)*W,"delta"))
                    delta_y.append(((j+1)*W, (i+1)*W,"delta"))
                    cv.rectangle(result, ((j+0)*W, (i+0)*W), ((j+1)*W, (i+1)*W), colors[singularity], 3)

                elif singularity == "loop":
                    my_input.append(singularity)
                    loop_x.append(((j+0)*W, (i+0)*W,"loop"))
                    loop_y.append(((j+1)*W, (i+1)*W,"loop"))
                    cv.rectangle(result, ((j+0)*W, (i+0)*W), ((j+1)*W, (i+1)*W), colors[singularity], 3)   
    print(my_input)
    print("-----Delta X-----")
    print(delta_x)
    print("-----Delta Y-----")
    print(delta_y)
    print("-----Loop X-----")
    print(loop_x)
    print("-----Loop Y-----")
    print(loop_y)

    deltaList =[t for t in delta_x if t[2].startswith('delta')]
    LoopList =[t for t in loop_y if t[2].startswith('loop')]
    print("-----Delta List-----")
    print(deltaList)
    print("-----Loop List-----")
    print(LoopList)
    deltaCheck=[]
    ycordinates=[]
    xcordinates=[]
    for delta in deltaList:
        last_element_index = len(delta)-1
        delta = delta[:last_element_index]
        if(delta[0] > delta[1]):
            deltaCheck.append(True)
        else:
            deltaCheck.append(False)

        for xcord in delta:
            xcordinates.append(xcord)
    

    for loop in LoopList:
        last_element_index = len(loop)-1
        loop = loop[:last_element_index]
        for ycord in loop:
            ycordinates.append(ycord)

    minYcord=0 if len(ycordinates)==0 else min(ycordinates)
    maxYCord =0 if len(ycordinates)==0 else max(ycordinates)
    maxXcord=0 if len(xcordinates)==0 else max(xcordinates)
    minXcord=0 if len(xcordinates)==0 else min(xcordinates)
   


    print(xcordinates)
    print(ycordinates)

    #if delta nd loop both are very close to each other it should behaves like 0 ridge count
    delta_x_len = len(delta_x)
    delta_y_len = len(delta_y)
    loop_x_len = len(loop_x)
    loop_y_len = len(loop_y)
    

    #zero ridge count conditions
    if(len(LoopList) == 0 or len(deltaList)==0):
        ridgeCount=0
    elif(len(LoopList) <= 3 and len(deltaList)<=3) :
        ridgeCount=0 
    # elif(delta_x_len >0  and delta_y_len >0 and loop_x_len >0 and loop_y_len >0):
    #     print(delta_x[delta_x_len-1][0])
    #     print(loop_x[loop_x_len-1][0])
    #     print(delta_y[delta_y_len-1][0])
    #     print(delta_x[delta_x_len-1][0])

    #     if ((delta_x[delta_x_len-1][0] - loop_x[loop_x_len-1][0])/16 <=2 and 
    #         (delta_y[delta_y_len-1][0] - loop_y[loop_y_len-1][0])/16 <=3):
    #      ridgeCount=0      
    elif (False not in deltaCheck):
     ridgeCount= (maxXcord- minYcord)/16 
    elif (maxYCord > maxXcord):
     ridgeCount= (maxYCord- minXcord)/16   
    elif(len(LoopList)==4 and len(deltaList)==4):
         ridgeCount= ((LoopList[len(LoopList) -1][0] - deltaList[len(deltaList) -1][0])/16) + ((LoopList[len(LoopList) -1][1] - deltaList[len(deltaList) -1][1])/16)
    elif(len(LoopList)==1 and len(deltaList)>1):
         ridgeCount= ((LoopList[len(LoopList) -1][1] - deltaList[len(deltaList) -1][1])/16)
    else:    
        ridgeCount= (LoopList[len(LoopList) -1][1] - deltaList[len(deltaList) -1][0])/16

    if ridgeCount == 1:
        ridgeCount=0

    print('ridgecount: '+ str(ridgeCount));   
    #return (result, ridgeCount)
    return result


if __name__ == '__main__':
    img = cv.imread('../test_img.png', 0)
    cv.imshow('original', img)
    angles = orientation.calculate_angles(img, 16, smoth=True)
    result = calculate_singularities(img, angles, 1, 16)
