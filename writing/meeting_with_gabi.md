
- Tommy check on the input data
- look at the x data from the training data

Steve and Olga
- 3D convolutions
- neighbourhoods defined in space and time

.values -> (time, variables, lat, lon)
.reshape -> (var, time, latlon (lat*lon))
.move_axis -> (latlon, var, time)

L13 - 16 (current)
ds_folder_to_np
train_iter
    out_x_current = []
    if nowcaster:
        feed this list

    return (x1,x2,x3), y

normalize everything first and then split it after the fact

NN = add another CNN.

Nowcast

Next steps:
- play with the input data
- meeting with USB santa barbara FEWSNET people
- get the nowcast done 
