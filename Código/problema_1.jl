using JuMP
using GLPK

function reader(filepath :: String)
    n = 0 # Nós
    m = 0 # Arestas
    D = 0 # D
    T = 0 # T

    distance_matrix = Vector{Vector{Int}}()
    line_list = Vector{Int}()

    open(filepath, "r") do f
        line_n = 1
        while !eof(f)
            line = readline(f)
            words = split(line)

            if line_n == 1
                n = parse(Int, String(words[1]))
                m = parse(Int, String(words[2]))
                D = parse(Int, String(words[3]))
                T = parse(Int, String(words[4]))
            end
            
            if line_n > 1 && line_n <= m+1
            elseif line_n != 1
                line_list = Vector{Int}()

                for a in 1:n
                    push!(line_list, parse(Int, String(words[a])))
                end

                vcat(distance_matrix, line_list)
            end

            line_n += 1
        end
    end

    return Instance(n, m, D, T, distance_matrix)
end

struct Instance
    n :: Int # Nós
    m :: Int # Arestas
    D :: Int # D
    T :: Int # T
    distance_matrix :: Vector{Vector{Int}} # Matriz de distâncias
end

dir = "./problema1-instancias/"

instance_list = ["instance_6_6_4_3.dat",         "instance_20_30_20_3.dat",
                 "instance_20_100_10_5.dat",     "instance_50_75_50_5.dat",
                 "instance_50_750_10_5.dat",     "instance_100_350_50_10.dat",
                 "instance_100_1000_25_15.dat",  "instance_250_3000_20_20.dat",
                 "instance_250_7500_10_25.dat",  "instance_500_2500_50_50.dat",
                 "instance_500_10000_15_50.dat", "instance_1000_10000_25_50.dat",
                 "instance_1000_50000_10_100.dat"]

for cur_instance in instance_list
    instance = reader(dir * cur_instance)

    n = instance.n
    m = instance.m
    D = instance.D
    T = instance.T
    d = instance.distance_matrix

    j = 0
    i = 0
    k = 0

    model = Model(GLPK.Optimizer)

    @variable(model, x[i, j], Bin)
    @variable(model, y[j], Bin)
    @variable(model, z[i, j, k], Bin)

    @objective(model, Min, sum(getindex(y, j) for j in 1:n))

    @constraint(model, c1, getindex(x, i, j) <= getindex(y, j))
    @constraint(model, c2, sum(getindex(x, i, j) for j in 1:n for i in 1:n) == 1)
    @constraint(model, c3, sum(getindex(x, i, j) for i in 1:n for j in 1:n) <= T)
    @constraint(model, c4, getindex(z, i, j, k) <= (getindex(x, i, k) + getindex(x, j, k))/2)
    @constraint(model, c5, getindex(z, i, j, k) >= getindex(x, i, j) + getindex(x, j, k)-1)
    @constraint(model, c6, getindex(d, i, j) <= D + M(1 - sum(getindex(z, i, j, k) for i in 1:n for j in 1:n for k in 1:n)))
          
    #print(model)
    optimize!(model)

    #@show termination_status(model)
    #@show primal_status(model)
    #@show dual_status(model)

    @show objective_value(model)
end