import numpy as np

class Componente():
    '''!
    @brief Classe abstrata base para todos os componentes de circuito
    @details Esta classe define a interface comum para todos os componentes de circuito elétrico.
    Ela implementa o padrão de projeto Template Method, onde cada componente específico
    deve implementar suas próprias estampas para os diferentes métodos de integração.
    
    A classe utiliza análise nodal modificada para resolver circuitos, onde cada componente
    contribui com sua estampa para as matrizes de condutância (Gn) e corrente (I).
    
    @author Equipe do Simulador de Circuitos
    @date 2025
    '''
    _linear = True
    _num_nos = 0
    _num_nos_mod = 0
    passo = 0.0 # passo de tempo, definido por Circuito.run()
    
    def __init__(self, name: str, nos: list[str]):
        '''!
        @brief Construtor da classe Componente
        @param name Nome único do componente no circuito
        @param nos Lista de nós conectados ao componente
        @exception AssertionError Se o número de nós não corresponder ao esperado
        @details Inicializa um componente com nome e nós específicos. Verifica se o número
        de nós fornecido corresponde ao número esperado para este tipo de componente.
        '''
        self._nos_mod = []
        assert len(nos) == self._num_nos
        self.name = name
        self.nos = nos

    @property
    def linear(self):
        '''!
        @property linear
        @brief Indica se o componente é linear ou não linear
        @return True se o componente é linear, False caso contrário
        @details Componentes lineares não requerem iteração de Newton-Raphson durante
        a simulação, enquanto componentes não lineares (como diodos e MOSFETs) requerem.
        '''
        return self._linear

    @property
    def num_nos_mod(self):
        '''!
        @property num_nos_mod
        @brief Retorna o número de nós extras necessários na análise nodal modificada
        @return Número de nós extras necessários
        @details Alguns componentes (como indutores e fontes de tensão) requerem nós
        extras para representar correntes de malha na análise nodal modificada.
        '''
        return self._num_nos_mod

    def set_nos_mod(self, nos_mod: list[int]):
        '''!
        @brief Define os nós extras necessários para análise nodal modificada
        @param nos_mod Lista dos índices dos nós extras nas matrizes Gn e I
        @exception AssertionError Se o número de nós extras não corresponder ao esperado
        @details Estes nós extras são usados para representar correntes de malha
        ou outras variáveis de estado necessárias para a análise.
        '''
        assert len(nos_mod) == self._num_nos_mod
        self._nos_mod = nos_mod

    def set_posicao_nos(self, posicoes: list[int]):
        '''!
        @brief Define as posições dos nós do componente nas matrizes do sistema
        @param posicoes Lista das posições dos nós nas matrizes Gn e I
        @details Estas posições são usadas para calcular corretamente as contribuições
        do componente para as matrizes do sistema de equações.
        '''
        self._posicao_nos = posicoes

    def __str__(self):
        '''!
        @brief Retorna representação do componente como linha da netlist
        @return String formatada representando o componente
        @details Esta representação é usada para salvar o circuito em arquivo netlist
        e deve seguir o formato padrão SPICE.
        '''
        return 'Componente' 

    def processa_argumentos_fonte(self, args):
        '''!
        @brief Processa argumentos de fontes de tensão ou corrente e coloca nos argumentos do objeto
        '''
        print(self.nos, args)
        if args[0] == 'DC':
            self.tipo = 'DC'
            self.nivel_dc = float(args[1])
        elif args[0] == 'SIN':
            self.tipo = 'SIN'
            self.nivel_dc = float(args[1])
            self.amplitude = float(args[2])
            self.frequencia = float(args[3])
            self.atraso = float(args[4])
            self.amortecimento = float(args[5])
            self.defasagem = float(args[6])
            self.ciclos = float(args[7])
        elif args[0] == 'PULSE':
            self.tipo = 'PULSE'
            self.amplitude_1 = float(args[1])
            self.amplitude_2 = float(args[2])
            self.atraso = float(args[3])
            self.tempo_descida = float(args[4])
            self.tempo_subida = float(args[5])
            self.tempo_ligado = float(args[6])
            self.periodo = float(args[7])
            self.ciclos = float(args[8])

    def calcular_valor_fonte(self, t):
        if self.tipo == 'DC':
            valor = self.nivel_dc
        elif self.tipo == 'SIN':
            tempo_total = self.atraso + self.ciclos/self.frequencia
            if t < self.atraso:
                valor = self.nivel_dc + self.amplitude*np.sin(np.pi*self.defasagem/180)
            elif t >= tempo_total:
                valor = self.nivel_dc + self.amplitude*np.exp(-self.amortecimento*(tempo_total - self.atraso))*np.sin(2*np.pi*self.frequencia*(tempo_total-self.atraso) + np.pi/180*self.defasagem)
            else:
                valor = self.nivel_dc + self.amplitude*np.exp(-self.amortecimento*(t - self.atraso))*np.sin(2*np.pi*self.frequencia*(t-self.atraso) + np.pi/180*self.defasagem)
        elif self.tipo == 'PULSE':
            tempo_total = self.ciclos*self.periodo
            valor = 0
        return valor

    def estampaBE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa do componente usando método Backward Euler
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais no tempo atual
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details Método abstrato que deve ser implementado por cada componente específico.
        O método Backward Euler é o padrão para simulação transiente.
        '''
        raise NotImplementedError
        
    def estampaTrap(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa do componente usando método Trapezoidal
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais no tempo atual
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details Método abstrato que deve ser implementado por cada componente específico.
        O método Trapezoidal oferece melhor precisão que Backward Euler.
        '''
        raise NotImplementedError
        
    def estampaFE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa do componente usando método Forward Euler
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais no tempo atual
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details Método abstrato que deve ser implementado por cada componente específico.
        O método Forward Euler é menos estável que Backward Euler.
        '''
        raise NotImplementedError

class Resistor(Componente):
    '''!
    @brief Representa um resistor linear no circuito
    @details O resistor é um componente linear que obedece à lei de Ohm: V = R*I.
    Sua estampa na análise nodal é bem definida e não depende do método de integração.
    
    @image html resistor_stamp.png "Estampa do Resistor"
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor do resistor
        @param name Nome único do resistor
        @param nos Lista com dois nós: [nó_positivo, nó_negativo]
        @param valor Resistência em ohms
        @details O resistor conecta dois nós e tem uma resistência específica.
        A corrente flui do nó positivo para o nó negativo.
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        '''!
        @brief Retorna representação do resistor como linha da netlist
        @return String no formato "R<nome> <nó1> <nó2> <valor>"
        @details Formato compatível com SPICE para resistor.
        '''
        return 'R' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa do resistor às matrizes do sistema
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais (não usado para resistor)
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details A estampa do resistor é a mesma para todos os métodos de integração:
        - Gn[i,i] += 1/R
        - Gn[i,j] -= 1/R
        - Gn[j,i] -= 1/R
        - Gn[j,j] += 1/R
        '''
        Gn[self._posicao_nos[0], self._posicao_nos[0]] += 1/self.valor
        Gn[self._posicao_nos[0], self._posicao_nos[1]] -= 1/self.valor
        Gn[self._posicao_nos[1], self._posicao_nos[0]] -= 1/self.valor
        Gn[self._posicao_nos[1], self._posicao_nos[1]] += 1/self.valor
        return Gn, I

class Indutor(Componente):
    '''!
    @brief Representa um indutor no circuito
    @details O indutor é um componente linear que armazena energia no campo magnético.
    Sua corrente e tensão estão relacionadas por: V = L * dI/dt.
    Na análise nodal modificada, requer um nó extra para representar a corrente.
    
    @image html inductor_stamp.png "Estampa do Indutor"
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 1
    
    def __init__(self, name: str, nos: list[str], valor: float, ic=0.0):
        '''!
        @brief Construtor do indutor
        @param name Nome único do indutor
        @param nos Lista com dois nós: [nó_positivo, nó_negativo]
        @param valor Indutância em henrys (H)
        @param ic Corrente inicial no indutor (padrão: 0.0 A)
        @details O indutor conecta dois nós e tem uma indutância específica.
        A corrente inicial é importante para simulação transiente.
        '''
        super().__init__(name, nos)
        self.valor = valor
        self.ic = ic
        self.corrente_atual = ic  # corrente no tempo atual

    def __str__(self):
        '''!
        @brief Retorna representação do indutor como linha da netlist
        @return String no formato "L<nome> <nó1> <nó2> <valor> [IC=<corrente_inicial>]"
        @details Formato compatível com SPICE para indutor.
        '''
        if self.ic != 0.0:
            return 'L' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor) + ' IC=' + str(self.ic)
        else:
            return 'L' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa do indutor usando método Backward Euler
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais no tempo atual
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details Usando Backward Euler: di/dt = (i(t+delta_t) - i(t))/delta_t
        A estampa inclui:
        - Contribuições para as tensões nodais
        - Equação da corrente do indutor
        - Termo histórico da corrente anterior
        '''
        
        # Equação da tensão: V1 - V2 = L * di/dt
        # Com Backward Euler: V1 - V2 = L * (i(t+Δt) - i(t))/Δt
        # Rearranjando: V1 - V2 - L/Δt * i(t+Δt) = -L/Δt * i(t)
        
        Gn[self._posicao_nos[0], self._nos_mod[0]] += 1
        Gn[self._posicao_nos[1], self._nos_mod[0]] -= 1


        Gn[self._nos_mod[0], self._posicao_nos[0]] -= 1
        Gn[self._nos_mod[0], self._posicao_nos[1]] += 1
        Gn[self._nos_mod[0], self._nos_mod[0]] += self.valor/self.passo

        I[self._nos_mod[0]] += (self.valor/self.passo)*self.ic
        return Gn, I

class Capacitor(Componente):
    '''!
    @brief Representa um capacitor no circuito
    @details O capacitor é um componente linear que armazena energia no campo elétrico.
    Sua corrente e tensão estão relacionadas por: I = C * dV/dt.
    Na análise nodal, sua estampa depende do método de integração utilizado.
    
    @image html capacitor_stamp.png "Estampa do Capacitor"
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    
    def __init__(self, name: str, nos: list[str], valor: float, ic=0.0):
        '''!
        @brief Construtor do capacitor
        @param name Nome único do capacitor
        @param nos Lista com dois nós: [nó_positivo, nó_negativo]
        @param valor Capacitância em farads (F)
        @param ic Corrente no capacitor (valor inicial: 0.0 A)
        @details O capacitor conecta dois nós e tem uma capacitância específica.
        A corrente inicial é importante para simulação transiente.
        '''
        super().__init__(name, nos)
        self.valor = valor
        self.ic = ic

    def __str__(self):
        '''!
        @brief Retorna representação do capacitor como linha da netlist
        @return String no formato "C<nome> <nó1> <nó2> <valor> [IC=<corrente_inicial>]"
        @details Formato compatível com SPICE para capacitor.
        '''
        if self.ic == 0.0:
            return 'C' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)
        else:
            return 'C' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor) + ' IC=' + str(self.ic)

    def estampaBE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa do capacitor usando método Backward Euler
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais no tempo atual
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details Usando Backward Euler: dV/dt = (V(t+delta_t) - V(t))/delta_t
        A estampa inclui:
        - Condutância equivalente: C/delta_t
        - Termo histórico da tensão anterior
        '''
        # Condutância equivalente do capacitor
        condutancia = self.valor / self.passo
        
        # Estampa da condutância
        Gn[self._posicao_nos[0], self._posicao_nos[0]] += condutancia
        Gn[self._posicao_nos[0], self._posicao_nos[1]] -= condutancia
        Gn[self._posicao_nos[1], self._posicao_nos[0]] -= condutancia
        Gn[self._posicao_nos[1], self._posicao_nos[1]] += condutancia

        # Termo histórico da tensão anterior
        I[self._posicao_nos[0]] += condutancia * self.ic
        I[self._posicao_nos[1]] -= condutancia * self.ic
        return Gn, I

class ResistorNaoLinear(Componente):
    '''!
    @brief Representa um resistor não linear com característica de 3 segmentos
    @details O resistor não linear é modelado por uma curva tensão-corrente definida
    por 4 pontos (V1,I1), (V2,I2), (V3,I3), (V4,I4), formando 3 segmentos lineares.
    A condutância é calculada dinamicamente baseada na tensão atual.
    
    @image html nonlinear_resistor.png "Característica do Resistor Não Linear"
    '''
    _linear = False
    _num_nos = 2
    _num_nos_mod = 0
    
    def __init__(self, name: str, nos: list[str], v1: float, i1: float, v2: float, i2: float, v3: float, i3: float, v4: float, i4: float):
        '''!
        @brief Construtor do resistor não linear
        @param name Nome único do resistor
        @param nos Lista com dois nós: [nó_positivo, nó_negativo]
        @param v1 Tensão do primeiro ponto (V)
        @param i1 Corrente do primeiro ponto (A)
        @param v2 Tensão do segundo ponto (V)
        @param i2 Corrente do segundo ponto (A)
        @param v3 Tensão do terceiro ponto (V)
        @param i3 Corrente do terceiro ponto (A)
        @param v4 Tensão do quarto ponto (V)
        @param i4 Corrente do quarto ponto (A)
        @details Os pontos devem estar ordenados por tensão crescente: V1 < V2 < V3 < V4
        '''
        super().__init__(name, nos)
        self.v1 = v1
        self.i1 = i1
        self.v2 = v2
        self.i2 = i2
        self.v3 = v3
        self.i3 = i3
        self.v4 = v4
        self.i4 = i4
        self.condutancia = Resistor(name + 'R', nos, 0)
        self.fonte = FonteCorrente(name + 'I', nos, ['DC', '0'])

    def set_posicao_nos(self, posicoes: list[int]):
        self.condutancia.set_posicao_nos(posicoes)
        self.fonte.set_posicao_nos(posicoes)
        super().set_posicao_nos(posicoes)

    def __str__(self):
        '''!
        @brief Retorna representação do resistor não linear como linha da netlist
        @return String no formato "N<nome> <nó1> <nó2> <v1> <i1> <v2> <i2> <v3> <i3> <v4> <i4>"
        @details Formato específico para resistor não linear com 4 pontos.
        '''
        return 'N' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.v1) + ' ' + str(self.i1) + ' ' + str(self.v2) + ' ' + str(self.i2) + ' ' + str(self.v3) + ' ' + str(self.i3) + ' ' + str(self.v4) + ' ' + str(self.i4)

    def estampaBE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa do resistor não linear às matrizes do sistema
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais no tempo atual
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details Calcula a condutância e corrente baseada na tensão atual,
        usando interpolação linear entre os pontos definidos.
        '''
        # TODO: Implementar cálculo da condutância e corrente baseada na tensão atual
        # Esta implementação requer acesso às tensões nodais atuais
        vab = tensoes[self._posicao_nos[0]] - tensoes[self._posicao_nos[1]]
        if vab > self.v3:
            g0 = (self.i4 - self.i3)/(self.v4 - self.v3)
            i0 = self.i4 - self.v4
        elif vab > self.v2:
            g0 = (self.i3 - self.i2)/(self.v3 - self.v2)
            i0 = self.i3 - self.v3
        else:
            g0 = (self.i2 - self.i1)/(self.v2 - self.v1)
            i0 = self.i2 - self.v2
        
        self.condutancia.valor = 1/g0
        self.fonte.args = ['DC', i0]
        self.fonte.calcular_valor_fonte(self.fonte.args)

        Gn, I = self.condutancia.estampaBE(Gn, I, t, tensoes)
        Gn, I = self.fonte.estampaBE(Gn, I, t, tensoes)
        return Gn, I

# tensao controlada por tensao
class FonteTensaoTensao(Componente):
    '''!
    @brief Representa uma fonte de tensão controlada por tensão (VCVS)
    @details A fonte de tensão controlada por tensão é um componente linear que
    gera uma tensão de saída proporcional à tensão de entrada. A relação é:
    Vout = A * Vin, onde A é o ganho de tensão.
    
    Na análise nodal modificada, requer um nó extra para representar a corrente
    da fonte de tensão.
    
    @image html vcvs_stamp.png "Estampa da Fonte de Tensão Controlada por Tensão"
    '''
    _linear = True
    _num_nos = 4
    _num_nos_mod = 1
    
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor da fonte de tensão controlada por tensão
        @param name Nome único da fonte
        @param nos Lista com quatro nós: [nó_saída_pos, nó_saída_neg, nó_controle_pos, nó_controle_neg]
        @param valor Ganho de tensão (adimensional)
        @details A fonte conecta quatro nós: dois para a saída e dois para o controle.
        O ganho determina a relação entre tensão de entrada e saída.
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        '''!
        @brief Retorna representação da fonte como linha da netlist
        @return String no formato "E<nome> <nó_saída_pos> <nó_saída_neg> <nó_controle_pos> <nó_controle_neg> <ganho>"
        @details Formato compatível com SPICE para fonte de tensão controlada por tensão.
        '''
        return 'E' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa da fonte de tensão controlada por tensão
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais no tempo atual
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details A estampa implementa a relação Vout = A * Vin usando um nó extra
        para representar a corrente da fonte de tensão.
        '''
        # Nó extra para corrente da fonte de tensão
        no_corrente = self._nos_mod[0]
        
        # Equação da tensão de saída: Vout = A * Vin
        # V1 - V2 = A * (V3 - V4)
        # Rearranjando: V1 - V2 - A*V3 + A*V4 = 0
        
        # Contribuições para a equação da tensão
        Gn[self._posicao_nos[0], no_corrente] += 1  # V1
        Gn[self._posicao_nos[1], no_corrente] -= 1  # V2
        Gn[no_corrente, self._posicao_nos[2]] += self.valor  # A*V3
        Gn[no_corrente, self._posicao_nos[3]] -= self.valor  # A*V4
        
        
        # Equação da corrente da fonte
        Gn[no_corrente, self._posicao_nos[0]] -= 1
        Gn[no_corrente, self._posicao_nos[1]] += 1
        
        return Gn, I
        

# corrente controlada por corrente
class FonteCorrenteCorrente(Componente):
    '''!
    @brief Esta classe implementa a Fonte de corrente controlada por corrente e sua estampa
    '''
    _linear = True
    _num_nos = 4
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor da Fonte de corrente controlada por corrente
        @param nos [no_mais, no_menos] nos da fonte
        @param valor ganho
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        '''!
        @brief Retorna representação da fonte como linha da netlist
        @return String no formato "F<nome> <nó_saída_pos> <nó_saída_neg> <nó_controle_pos> <nó_controle_neg> <ganho>"
        @details Formato compatível com SPICE para fonte de tensão controlada por tensão.
        '''
        return 'F' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, t, tensoes):
        return Gn, I

# corrente controlada por tensao
class FonteCorrenteTensao(Componente):
    '''!
    @brief Esta classe implementa a Fonte de corrente controlada por tensao e sua estampa
    '''
    _linear = True
    _num_nos = 4
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor da Fonte de corrente controlada por tensao
        @param nos [no_mais, no_menos] nos da fonte
        @param valor ganho
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        '''!
        @brief Retorna representação da fonte como linha da netlist
        @return String no formato "G<nome> <nó_saída_pos> <nó_saída_neg> <nó_controle_pos> <nó_controle_neg> <ganho>"
        @details Formato compatível com SPICE para fonte de tensão controlada por tensão.
        '''
        return 'G' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa da fonte de corrente controlada por tensão
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais no tempo atual
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details A estampa implementa a relação Iout = G * Vin
        '''
        # Equação da corrente: Iout = G * (V3 - V4)
        # Contribuições para os nós de saída
        Gn[self._posicao_nos[0], self._posicao_nos[2]] += self.valor  # +G*V3
        Gn[self._posicao_nos[0], self._posicao_nos[3]] -= self.valor  # -G*V4
        Gn[self._posicao_nos[1], self._posicao_nos[2]] -= self.valor  # -G*V3
        Gn[self._posicao_nos[1], self._posicao_nos[3]] += self.valor  # +G*V4
        
        return Gn, I

# tensao controlada por corrente
class FonteTensaoCorrente(Componente):
    '''!
    @brief Esta classe implementa a Fonte de tensao controlada por corrente e sua estampa
    '''
    _linear = True
    _num_nos = 4
    _num_nos_mod = 2
    def __init__(self, name: str, nos: list[str], valor: float):
        '''!
        @brief Construtor da Fonte de tensao controlada por corrente
        @param nos [no_mais, no_menos] nos da fonte
        @param valor ganho
        '''
        super().__init__(name, nos)
        self.valor = valor

    def __str__(self):
        '''!
        @brief Retorna representação da fonte como linha da netlist
        @return String no formato "H<nome> <nó_saída_pos> <nó_saída_neg> <nó_controle_pos> <nó_controle_neg> <ganho>"
        @details Formato compatível com SPICE para fonte de tensão controlada por tensão.
        '''
        return 'H' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + str(self.valor)

    def estampaBE(self, Gn, I, t, tensoes):
        '''!
        @brief Adiciona a estampa da fonte de tensão controlada por corrente
        @param Gn Matriz de condutância do sistema
        @param I Vetor de correntes do sistema
        @param t instante de tempo atual
        @param tensoes Vetor de tensões nodais no tempo atual
        @return Tupla (Gn, I) com as matrizes atualizadas
        @details A estampa implementa a relação Vout = H * Vin usando dois nós extra
        para representar a corrente da fonte de tensão e do nó de controle.
        '''
        # Nós extras para as variáveis auxiliares
        no_jx = self._nos_mod[0]  # jx
        no_jy = self._nos_mod[1]  # jy
        
        # Equação da tensão de saída: Vout = Rm * Iin
        # V1 - V2 = Rm * (corrente de controle)
        
        # Contribuições para a equação da tensão
        Gn[self._posicao_nos[0], no_jx] -= 1  # V1
        Gn[self._posicao_nos[1], no_jx] += 1  # V2
        Gn[self._posicao_nos[2], no_jy] -= 1  # V3
        Gn[self._posicao_nos[3], no_jy] += 1  # V4
        
        # Equação da corrente jx
        Gn[no_jx, self._posicao_nos[0]] += 1
        Gn[no_jx, self._posicao_nos[1]] -= 1
        
        # Equação da corrente jy
        Gn[no_jy, self._posicao_nos[2]] += 1
        Gn[no_jy, self._posicao_nos[3]] -= 1
        Gn[no_jy, no_jx] += self.valor
        
        return Gn, I

class Diodo(Componente):
    '''!
    @brief Esta classe implementa o Diodo e sua estampa
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 2
    def __init__(self, name: str, nos: list[str]):
        '''!
        @brief Construtor do Diodo
        @param nos [no_mais, no_menos] nos do diodo
        '''
        super().__init__(name, nos)
        self.condutancia = Resistor(name + 'R', nos, 0)
        self.fonte = FonteCorrente(name + 'I', nos, ['DC', '0'])

    def set_posicao_nos(self, posicoes: list[int]):
        self.condutancia.set_posicao_nos(posicoes)
        self.fonte.set_posicao_nos(posicoes)
        super().set_posicao_nos(posicoes)

    def __str__(self):
        '''!
        @brief Retorna representação do diodo como linha da netlist
        @return String no formato "N<nome> <nó+> <nó->"
        @details Formato específico para diodo com dois terminais.
        '''
        return 'D' + self.name + ' ' + ' '.join(str(no) for no in self.nos)

    def estampaBE(self, Gn, I, t, tensoes):
        vab = tensoes[self._posicao_nos[0]] - tensoes[self._posicao_nos[1]]
        g0 = 3.7751345e-14*np.exp(vab/25e-3)/25e-3
        id = 3.7751345e-14*(np.exp(vab/25e-3)-1)-g0*vab

        self.condutancia.valor = 1/g0
        self.fonte.args = ['DC', id]
        self.fonte.calcular_valor_fonte(self.fonte.args)

        Gn, I = self.condutancia.estampaBE(Gn, I, t, tensoes)
        Gn, I = self.fonte.estampaBE(Gn, I, t, tensoes)
        return Gn, I

class AmpOp(Componente):
    '''!
    @brief Esta classe implementa o Amplificador Operacional ideal e sua estampa
    '''
    _linear = True
    _num_nos = 3
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str]):
        '''!
        @brief Construtor do Amplificador Operacional
        @param nos [no_mais, no_menos, no_saida] nos do amp op
        '''
        super().__init__(name, nos)

    def __str__(self):
        '''!
        @brief Retorna representação do amplificador operacional ideal como linha da netlist
        @return String no formato "O<nome> <nó+> <nó-> <nó-saida>"
        @details Formato específico para amplificador operacional ideal com dois terminais.
        '''
        return 'O' + self.name + ' ' + ' '.join(str(no) for no in self.nos)

    def estampaBE(self, Gn, I, t, tensoes):
        # Nó extra para corrente de saída do amp op
        no_corrente = self._nos_mod[0]
        
        # Equação da tensão de saída: Vout = A * (V+ - V-)
        # Para amp op ideal: A = infinito, então V+ = V-
        # Equação: V+ - V- = 0
        
        # Contribuições para a equação V+ - V- = 0
        Gn[self._posicao_nos[0], no_corrente] -= 1  # -V+
        Gn[self._posicao_nos[1], no_corrente] += 1  # +V-
        
        # Equação da corrente de saída
        Gn[no_corrente, self._posicao_nos[0]] += 1   # +V+
        Gn[no_corrente, self._posicao_nos[1]] -= 1   # -V-
        Gn[no_corrente, self._posicao_nos[2]] += 1   # +Vout
        
        return Gn, I

class Mosfet(Componente):
    '''!
    @brief Esta classe implementa o transistor MOSFET e sua estampa
    '''
    def __init__(self):
        '''!
        @brief Construtor do Mosfet
        '''
        raise NotImplementedError

class FonteCorrente(Componente):
    '''!
    @brief Esta classe implementa a Fonte de corrente e sua estampa
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 0
    def __init__(self, name: str, nos: list[str], args: list):
        '''!
        @brief Construtor Fonte de corrente
        @param nos [no_mais, no_menos] nos da fonte
        @param args parametros no estilo SPICE
        '''
        super().__init__(name, nos)
        self.processa_argumentos_fonte(args)
        self.args = args

    def __str__(self):
        '''!
        @brief Retorna representação da fonte de corrente como linha da netlist
        @return String no formato "I<nome> <nó+> <nó-> <args>"
        @details Para fontes, temos três possibilidades para args:
        - DC <valor> : Fonte DC de <valor> amperes
        - SIN <valor-dc> <amplitude> <frequência> <atraso> <amortecimento> <defasagem> <ciclos> : Fonte senoidal
        - PULSE <amplitude-1> <amplitude-2> <atraso> <tempo-subida <tempo-descida> <tempo-ligado> <período> <ciclos> : Fonte pulsada
        '''
        return 'I' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + ' '.join(self.args)

    def estampaBE(self, Gn, I, t, tensoes):
        # Condutância equivalente do capacitor
        corrente = self.calcular_valor_fonte(t)

        # Termo histórico da tensão anterior
        I[self._posicao_nos[0]] += corrente
        I[self._posicao_nos[1]] -= corrente
        return Gn, I

class FonteTensao(Componente):
    '''!
    @brief Esta classe implementa a Fonte de tensao e sua estampa
    '''
    _linear = True
    _num_nos = 2
    _num_nos_mod = 1
    def __init__(self, name: str, nos: list[str], args: list):
        '''!
        @brief Construtor da Fonte de tensao
        @param nos [no_mais, no_menos] nos da fonte
        @param args parametros no estilo SPICE
        '''
        super().__init__(name, nos)
        self.processa_argumentos_fonte(args)
        self.args = args

    def __str__(self):
        '''!
        @brief Retorna representação da fonte de corrente como linha da netlist
        @return String no formato "V<nome> <nó+> <nó-> <args>"
        @details Para fontes, temos três possibilidades para args:
        - DC <valor> : Fonte DC de <valor> volts
        - SIN <valor-dc> <amplitude> <frequência> <atraso> <amortecimento> <defasagem> <ciclos> : Fonte senoidal
        - PULSE <amplitude-1> <amplitude-2> <atraso> <tempo-subida <tempo-descida> <tempo-ligado> <período> <ciclos> : Fonte pulsada
        '''
        return 'V' + self.name + ' ' + ' '.join(str(no) for no in self.nos) + ' ' + ' '.join(self.args)

    def estampaBE(self, Gn, I, t, tensoes):
        # Condutância equivalente do capacitor
        tensao = self.calcular_valor_fonte(t)
        
        # Estampa da condutância
        Gn[self._posicao_nos[0], self._nos_mod[0]] += 1
        Gn[self._posicao_nos[1], self._nos_mod[0]] -= 1
        Gn[self._nos_mod[0], self._posicao_nos[0]] -= 1
        Gn[self._nos_mod[0], self._posicao_nos[1]] += 1

        # Termo histórico da tensão anterior
        I[self._nos_mod[0]] -= tensao
        return Gn, I