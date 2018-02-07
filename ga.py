#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generic algorithm for optimizing problem."""

__author__ = """牛阿 https://www.zhihu.com/people/Enhuiz/
                modified by Clarence Zhuo"""

import math, random

class GA(object):

    def __init__(self, target, *, count=300, lo=0, hi=1, eps=1e-4):

        self.count = count              # 种群大小
        self.fitness_function = target  # 适应度函数
        self.lower_bound = lo           # 区间左端点
        self.upper_bound = hi           # 区间右端点
        self.length = math.ceil(math.log2((hi-lo)/eps+1)) # 染色体长度
        self.step = (hi - lo) / ((1 << self.length)-1)    # 精度
        self.population = self.gen_population()           # 初始化种群
        self.generation = 0              # 当前进化次数

    def evolve(self, retain_rate=0.2, random_select_rate=0.5, mutation_rate=0.01):
        """
        进化
        对当前种群进行变异、选择、交叉并生成新一代种群
        """
        self.mutate(mutation_rate)
        parents = self.select(retain_rate, random_select_rate)
        self.crossover(parents)
        self.generation += 1

    def gen_chromosome(self):
        """
        随机生成长度为 length 的染色体，每个基因以 1/2 的概率取值 0 或 1
        这里用一个 bit 表示一个基因
        """
        chromosome = 0
        for i in range(self.length):
            if random.randint(0, 1):
                chromosome |= (1 << i)
        return chromosome

    def gen_population(self):
        """
        获取初始种群 (一个含有 count 个长度为 length 的染色体的列表)
        """
        return [self.gen_chromosome() for i in range(self.count)]

    def fitness(self, chromosome):
        """
        计算适应度，将染色体解码为 lower_bound ~ upper_bound 之间的数字， 
        代入函数计算。默认情况下数值越大，适应度越高
        """
        x = self.decode(chromosome)
        return self.fitness_function(x)

    def select(self, retain_rate, random_select_rate):
        """
        选择
        先对适应度从大到小排序，选出存活的染色体
        再进行随机选择，选出适应度虽小，但是幸存的个体
        """
        # 对适应度从大到小排序 # 只要找出前 retain_length 个！
        graded = sorted(self.population, key=self.fitness, reverse=True)

        # 选出适应性强的染色体
        retain_length = int(len(graded) * retain_rate)
        parents = graded[:retain_length]

        # 选出适应性不强，但是幸存的染色体
        for chromosome in graded[retain_length:]:
            if random.random() < random_select_rate:
                parents.append(chromosome)
        return parents

    def crossover(self, parents):
        """
        染色体的交叉、繁殖，生成新一代的种群
        """
        # 新出生的孩子，最终会被加入存活下来的父母之中，形成新一代种群
        children = []

        # 需要繁殖的孩子的量
        target_count = len(self.population) - len(parents)

        # 开始根据需要的量进行繁殖
        while len(children) < target_count:
            male = random.randint(0, len(parents)-1)
            female = random.randint(0, len(parents)-1)
            if male != female:

                # 随机选取交叉点, 注意取值范围是 0 ~ length
                cross_pos = random.randint(0, self.length)

                # 生成掩码 (cross_pos 个 1)，方便位操作
                mask = (1 << cross_pos) - 1
                male = parents[male]
                female = parents[female]

                # 孩子将获得父亲在交叉点前的基因和母亲在交叉点(含)后的基因
                child = ((male & mask) | (female & ~mask)) & ((1 << self.length) - 1)
                children.append(child)

        # 经过繁殖，孩子与父母的数量与原始种群数量相等
        self.population = parents + children

    def mutate(self, rate):
        """
        变异
        种群中所有个体的所有基因以 rate 的概率改变 (即反转这个 bit)
        """
        for chromosome in self.population:
            if random.random() < rate:
                chromosome ^= 1 << random.randint(0, self.length-1)

    def decode(self, chromosome):
        """
        解码染色体，将二进制转化为目标区间中的值
        """
        return self.lower_bound + chromosome * self.step

    def result(self):
        """
        返回当前代的最优值，即使 fitness 取最大值的染色体
        """
        if self.generation == 0:
            return max(self.population, key=self.fitness)
        return self.population[0]

def variant(L):
    mean = sum(L) / len(L)
    return sum((x-mean)**2 for x in L) / len(L)

if __name__ == '__main__':
    ga = GA(\
        lambda x: x + 10*math.sin(5*x) + 7*math.cos(4*x),\
        count = 300,\
        lo = 0,\
        hi = 9,\
        eps = 1e-4\
    )
    fitness_list = []
    for n in range(10):
        ga.evolve()
        fitness_list.append(ga.fitness(ga.result()))

    while (variant(fitness_list) >= ga.step**2):
        ga.evolve()
        fitness_list.pop(0)
        fitness_list.append(ga.fitness(ga.result()))

    chromosome = ga.result()
    x = ga.decode(chromosome)
    y = ga.fitness_function(x)
    print('generation: %d' % ga.generation)
    print('best chromosome: %s' % bin(chromosome))
    print('best value of x: %f' % x)
    print('best fitness: %f' % y)

