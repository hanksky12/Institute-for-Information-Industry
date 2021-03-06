#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 導入 tensorflow
import tensorflow as tf 


# In[2]:


#Fetch
input1 = tf.constant(3.0)
input2 = tf.constant(2.0)
input3 = tf.constant(5.0)

add = tf.add(input2,input3)
mul = tf.multiply(input1,add)

with tf.Session() as sess:
    result = sess.run([mul,add])   # 同時運行兩個 op
    print(result)


# In[3]:


#Feed
#  創建佔位符
input1 = tf.placeholder(tf.float32)
input2 = tf.placeholder(tf.float32)
output = tf.multiply(input1,input2)

with tf.Session() as sess:
    # feed 的數據以字典的形式傳入
    print(sess.run(output,feed_dict = {input1:[7.],input2:[2.0]}))


# In[ ]:




