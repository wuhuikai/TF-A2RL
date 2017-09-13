import tensorflow as tf

def conv(input, kernel, biases, k_h, k_w, c_o, s_h, s_w,  padding="VALID", group=1):
    '''From https://github.com/ethereon/caffe-tensorflow
    '''
    convolve = lambda i, k: tf.nn.conv2d(i, k, [1, s_h, s_w, 1], padding=padding)

    if group==1:
        conv = convolve(input, kernel)
    else:
        input_groups = tf.split(input, group, 3)
        kernel_groups = tf.split(kernel, group, 3)
        output_groups = [convolve(i, k) for i,k in zip(input_groups, kernel_groups)]
        conv = tf.concat(output_groups, 3)
    return  tf.nn.bias_add(conv, biases)

def vfn_rl(x, variable_dict, global_feature=None, h=None, c=None, embedding_dim=1000):
    ########################## VFN ##################################
    ######################## Layer 1 ################################
    ## conv1
    #  conv(11, 11, 96, 4, 4, padding='VALID', name='conv1')
    k_h = 11; k_w = 11; c_o = 96; s_h = 4; s_w = 4
    conv1W = variable_dict["c1w"]
    conv1b = variable_dict["c1b"]
    conv1_in = conv(x, conv1W, conv1b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=1)
    conv1 = tf.nn.relu(conv1_in)
    ## lrn1
    #  lrn(2, 2e-05, 0.75, name='norm1')
    radius = 2; alpha = 2e-05; beta = 0.75; bias = 1.0
    lrn1 = tf.nn.local_response_normalization(conv1,
                                              depth_radius=radius,
                                              alpha=alpha,
                                              beta=beta,
                                              bias=bias)
    ## maxpool1
    #  max_pool(3, 3, 2, 2, padding='VALID', name='pool1')
    k_h = 3; k_w = 3; s_h = 2; s_w = 2; padding = 'VALID'
    maxpool1 = tf.nn.max_pool(lrn1, ksize=[1, k_h, k_w, 1], strides=[1, s_h, s_w, 1], padding=padding)

    ######################## Layer 2 ################################
    ## conv2
    #  conv(5, 5, 256, 1, 1, group=2, name='conv2')
    k_h = 5; k_w = 5; c_o = 256; s_h = 1; s_w = 1; group = 2
    conv2W = variable_dict["c2w"]
    conv2b = variable_dict["c2b"]
    conv2_in = conv(maxpool1, conv2W, conv2b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=group)
    conv2 = tf.nn.relu(conv2_in)
    ## lrn2
    #  lrn(2, 2e-05, 0.75, name='norm2')
    radius = 2; alpha = 2e-05; beta = 0.75; bias = 1.0
    lrn2 = tf.nn.local_response_normalization(conv2,
                                              depth_radius=radius,
                                              alpha=alpha,
                                              beta=beta,
                                              bias=bias)
    ## maxpool2
    #  max_pool(3, 3, 2, 2, padding='VALID', name='pool2')
    k_h = 3; k_w = 3; s_h = 2; s_w = 2; padding = 'VALID'
    maxpool2 = tf.nn.max_pool(lrn2, ksize=[1, k_h, k_w, 1], strides=[1, s_h, s_w, 1], padding=padding)

    ######################## Layer 3 ################################
    ## conv3
    #  conv(3, 3, 384, 1, 1, name='conv3')
    k_h = 3; k_w = 3; c_o = 384; s_h = 1; s_w = 1; group = 1
    conv3W = variable_dict["c3w"]
    conv3b = variable_dict["c3b"]
    conv3_in = conv(maxpool2, conv3W, conv3b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=group)
    conv3 = tf.nn.relu(conv3_in)

    ######################## Layer 4 ################################
    ## conv4
    #  conv(3, 3, 384, 1, 1, group=2, name='conv4')
    k_h = 3; k_w = 3; c_o = 384; s_h = 1; s_w = 1; group = 2
    conv4W = variable_dict["c4w"]
    conv4b = variable_dict["c4b"]
    conv4_in = conv(conv3, conv4W, conv4b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=group)
    conv4 = tf.nn.relu(conv4_in)

    ######################## Layer 5 ################################
    ## conv5
    #  conv(3, 3, 256, 1, 1, group=2, name='conv5')
    k_h = 3; k_w = 3; c_o = 256; s_h = 1; s_w = 1; group = 2
    conv5W = variable_dict["c5w"]
    conv5b = variable_dict["c5b"]
    conv5_in = conv(conv4, conv5W, conv5b, k_h, k_w, c_o, s_h, s_w, padding="SAME", group=group)
    conv5 = tf.nn.relu(conv5_in)
    ## maxpool5
    #  max_pool(3, 3, 2, 2, padding='VALID', name='pool5')
    with tf.variable_scope("conv5"):
        k_h = 3; k_w = 3; s_h = 2; s_w = 2; padding = 'VALID'
        maxpool5 = tf.nn.max_pool(conv5, ksize=[1, k_h, k_w, 1], strides=[1, s_h, s_w, 1], padding=padding)
        bn5 = tf.contrib.layers.flatten(maxpool5)

    ####################### Layer 6 ################################
    fc6W =  variable_dict["fc6w"]
    fc6b = variable_dict["fc6b"]
    fc6 = tf.nn.relu_layer(bn5, fc6W, fc6b)

    if global_feature is None:
        return fc6

    ########################### RL ##################################
    x_rl = tf.concat([global_feature, fc6], axis=1)
    ############## Layer 1 #################
    fc1W = variable_dict['fc1.weight'].T
    fc1b = variable_dict['fc1.bias']
    fc1 = tf.nn.relu_layer(x_rl, fc1W, fc1b)

    ############## Layer 2 #################
    fc2W = variable_dict['fc2.weight'].T
    fc2b = variable_dict['fc2.bias']
    fc2 = tf.nn.relu_layer(fc1, fc2W, fc2b)

    ############## Layer 3 #################
    fc3W = variable_dict['fc3.weight'].T
    fc3b = variable_dict['fc3.bias']
    fc3 = tf.nn.relu_layer(fc2, fc3W, fc3b)

    ############## LSTM #################
    W = tf.matmul(fc3, variable_dict['lstm.weight_ih'].T) + variable_dict['lstm.bias_ih'] +\
        tf.matmul(h, variable_dict['lstm.weight_hh'].T) + variable_dict['lstm.bias_hh']
    i, f, g, o = tf.split(W, 4, axis=1)
    i = tf.sigmoid(i); f = tf.sigmoid(f); g = tf.tanh(g); o = tf.sigmoid(o);
    c = f*c + i*g
    h = o*tf.tanh(c)

    ############## Action #################
    action1w = variable_dict['action_fc.weight'].T
    action1b = variable_dict['action_fc.bias']
    action = tf.multinomial(tf.matmul(h, action1w) + action1b, 1)

    return action, h, c