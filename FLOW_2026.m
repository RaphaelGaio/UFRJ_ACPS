clc
clear all
close all

%%

CASO = 4; % 1 - EXEMPLO 1 AULA 2
          % 2 - EXEMPLO 2 AULA 2
          % SISTEMA DE 30 BARRAS
%% Dados de Entrada

if CASO==1
    %        Barra  Tipo  V(pu)  Teta(º)  PG      QG      QN(min)  QM(máx)   PD       QD     SHUNT       
    DBAR = [  1      2    1.00     0      0       0         -999    999       0        0        0
              2      1    1.00     0      0       0         -999   999     0.40        0        0];
    
    %%
     %        De  Para   Rkm(%)  Xkm(%)   Bsh(MVAr)  TAP  DEFASAGEM    PkmMAX      
    DLIN=[    1    2      20      100       0.08         1      0           0];
    % Potência Base
    Pbase = 1;
    
    tol = 0.003; % Critério de Convergência do Anarede para Resíduo de P e Q = 0.01 MW/Mvar
end

if CASO==2
    %        Barra  Tipo  V(pu)  Teta(º)  PG      QG      QN(min)  QM(máx)   PD       QD     SHUNT       
    DBAR = [  1      2    1.00     0      0       0         -999    999       0        0        0
              2      0    1.00     0      0       0         -999   999      0.30*1       -0.07*1        0];
    
    %%
     %        De  Para   Rkm(%)  Xkm(%)   Bsh(MVAr)  TAP  DEFASAGEM    PkmMAX      
    DLIN=[    1    2      20      100       0.04         1      0           0];
    % Potência Base
    Pbase = 1;
    
    tol = 0.003; % Critério de Convergência do Anarede para Resíduo de P e Q = 0.01 MW/Mvar
end

%%
if CASO==3
    %        Barra  Tipo  V(pu)  Teta(º)  PG      QG      QN(min)  QM(máx)   PD       QD     SHUNT       
    DBAR  = [  1     2    1.060    0    260.2  -16.1        0       0        0        0     0
               2     1    1.043   -5     40.0    50       -40      50       21.7    12.7   0
               3     0    1.021   -7      0       0         0       0        2.4     1.2    0
               4     0    1.012   -9      0       0         0       0        7.6     1.6    0
               5     1    1.010  -14      0     37.0      -40      40        94.2    19.0   0
               6     0    1.010  -11      0       0         0       0        0       0     0
               7     0    1.002  -13      0       0         0       0        22.8    10.9   0
               8     1    1.010  -12      0     37.3      -10      40        30.0    30.0   0
               9     0    1.051  -14      0       0         0       0        0       0     0
               10    0    1.045  -15      0       0         0       0         5.8     2.0  19.0
               11    1    1.082  -14      0     16.2       -6      24         0.0     0.0    0
               12    0    1.057  -15      0       0         0       0        11.2    7.5    0
               13    1    1.071  -15      0     10.6       -6      24         0.0     0.0    0
               14    0    1.042  -16      0       0         0       0         6.2     1.6    0
               15    0    1.038  -16      0       0         0       0         8.2     2.5    0
               16    0    1.045  -15      0       0         0       0         3.5     1.8    0
               17    0    1.040  -16      0       0         0       0         9.0     5.8    0
               18    0    1.028  -16      0       0         0       0         3.2     0.9    0
               19    0    1.026  -17      0       0         0       0         9.5     3.4    0
               20    0    1.030  -16      0       0         0       0         2.2     0.7    0
               21    0    1.033  -16      0       0         0       0        17.5   11.2    0
               22    0    1.033  -16      0       0         0       0         0.0    0.0    0
               23    0    1.027  -16      0       0         0       0         3.2    1.6    0
               24    0    1.021  -16      0       0         0       0         8.7    6.7  4.30
               25    0    1.017  -16      0       0         0       0         0.0    0.0    0
               26    0    1.000  -16      0       0         0       0         3.5    2.3    0
               27    0    1.023  -15      0       0         0       0         0.0    0.0    0
               28    0    1.007  -11      0       0         0       0         0.0    0.0    0
               29    0    1.003  -17      0       0         0       0         2.4    0.9    0
               30    0    0.992  -17      0       0         0       0        10.6    1.9    0]; 
           
    
        
          
          
          
    %        De  Para   Rkm(%)  Xkm(%)   Bsh(MVAr)  TAP  DEFASAGEM    PkmMAX      
    DLIN  = [ 1   2     1.920   5.750      5.280     1      0          200
              1   3     4.520  16.520      4.080     1      0          90
              2   4     5.700  17.370      3.680     1      0          50
              3   4     1.320   3.790      0.840     1      0          90
              2   5     4.720  19.830      4.180     1      0          100
              2   6     5.810  17.630      3.740     1      0          80
              4   6     1.190   4.140      0.900     1      0          80
              5   7     4.600  11.600      2.040     1      0          30
              6   7     2.670   8.200      1.700     1      0          40
              6   8     1.200   4.200      0.900     1      0          40
              6   9     0      20.800       0      0.978    0          40
              6   10    0      55.600       0      0.969    0          30
              9   11    0      20.800       0        1      0          50
              9   10    0      11.000       0        1      0          40
              4   12    0      25.600       0      0.932    0          50  
              12  13    0      14.000       0        1      0          50
              12  14    12.31  25.590       0        1      0          20
              12  15    6.620  13.040       0        1      0          20
              12  16    9.450  19.870       0        1      0          20
              14  15   22.100  19.970       0        1      0          10
              16  17   5.240   19.230       0        1      0          10
              15  18  10.730   21.850       0        1      0          10
              18  19   6.390   12.920       0        1      0          10
              19  20   3.400    6.800       0        1      0          10
              10  20   9.360   20.900       0        1      0          10
              10  17   3.240    8.450       0        1      0          10
              10  21   3.480    7.490       0        1      0          20
              10  22   7.270   14.990       0        1      0          20
              21  22   1.160    2.360       0        1      0          20
              15  23  10.000   20.200       0        1      0          20
              22  24  11.500   17.900       0        1      0          20
              23  24  13.200   27.000       0        1      0          20
              24  25  18.850   32.920       0        1      0          20
              25  26  25.440   38.000       0        1      0          20
              25  27  10.930   20.870       0        1      0          20
              28  27    0      39.600       0       0.968   0          20
              27  29  21.980   41.530       0        1      0          20
              27  30  32.020   60.270       0        1      0          20
              29  30  23.990   45.330       0        1      0          20
              8   28  6.360    20.000      4.280     1      0          20
              6   28  1.690    5.990       1.300     1      0          20];
    
    %Potência Base
    Pbase = 100;
    tol = 0.01/Pbase; % Critério de Convergência do Anarede para Resíduo de P e Q = 0.01 MW/Mvar
end

if CASO==4
    %        Barra  Tipo  V(pu)  Teta(º)  PG      QG      QN(min)  QM(máx)   PD       QD     SHUNT       
    DBAR = [  1      2    1.00     0      0       0         -999    999       0        0        0
              2      0    1.00     0      0       0         -999   999      0.40     -0.10        0];
    
    %%
     %        De  Para   Rkm(%)  Xkm(%)   Bsh(MVAr)  TAP  DEFASAGEM    PkmMAX      
    DLIN=[    1    2      10      50       0.08         1      0           0];
    % Potência Base
    Pbase = 1;
    
    tol = 0.003; % Critério de Convergência do Anarede para Resíduo de P e Q = 0.01 MW/Mvar
end


%%

% Nº de Barras:
NBAR = length(DBAR(:,1));

% Número de Linhas
[NLIN,AUX]=size(DLIN);



%%
%**************************************************************************
%   SEPARAÇÃO EM VETORES
%**************************************************************************

% Divisão de DBAR em vetores (Teta em radianos)
TIPO = DBAR(:,2); 
V = DBAR(:,3); 
TETA = DBAR(:,4)*pi/180;
PG = DBAR(:,5)/Pbase;
QG = DBAR(:,6)/Pbase;
QN = DBAR(:,7)/Pbase;
QM = DBAR(:,8)/Pbase;
PD = DBAR(:,9)/Pbase; 
QD = DBAR(:,10)/Pbase; 
SHUNT = DBAR(:,11)/Pbase;

% Divisão de DLIN em vetores
DE = DLIN(:,1);
PARA = DLIN(:,2);
R = DLIN(:,3)/100;
X = DLIN(:,4)/100;
BSH =(DLIN(:,5)/2)/Pbase; 
DEFAS = DLIN(:,7);
TAP = DLIN(:,6); % Trafos t:1 no anarede

%% Algoritmo de Inicialização

iteracao = 0;    % Número de Iterações

Pesp = PG-PD;    % Valor Especificado de P (Líquido)
Qesp = QG-QD;    % Valor Especificado de Q (Líquido)

Ybarra = zeros(NBAR); % Inicialização de Ybarra

H = zeros(NBAR); % Submatriz de Jac = dP/dTeta
N = zeros(NBAR); % Submatriz de Jac = dP/dV
M = zeros(NBAR); % Submatriz de Jac = dQ/dTeta
L = zeros(NBAR); % Submatriz de Jac = dQ/dV

PV(:,1) = find(TIPO(:,1)==1); % Seleção dos números das barras PV

NPV = length(PV); % Quantidade de Barras PV

Vesp = V; % Tensão Especificada são as Tensões de Entrada Iniciais

FLUXO=zeros(NLIN,5);
FLUXO(:,3) = DLIN(:,8); % Valores máximos de fluxo na linha entre as barras k e m

%% MONTAGEM DE YBARRA

% Admitância Série
Ykm = 1./(R+1i*X);
% Admitância Shunt
Bsh = 1i*BSH;

% Montagem de Ybarra sem elementos shunts de barra
for k=1:NLIN
    x=DE(k); y=PARA(k);
    Ybarra(x,x) = Ybarra(x,x) + Bsh(k) + ((1/TAP(k))^2)*Ykm(k);
    Ybarra(y,y) = Ybarra(y,y) + Bsh(k) + Ykm(k);
    Ybarra(x,y) = Ybarra(x,y) - Ykm(k)*(1/TAP(k))*exp(-1i*DEFAS(k));
    Ybarra(y,x) = Ybarra(y,x) - Ykm(k)*(1/TAP(k))*exp(1i*DEFAS(k));    
end

% Inserção dos elementos shunts de barra
for k=1:NBAR
    Ybarra(k,k) = Ybarra(k,k) + 1i*SHUNT(k);
end

% Parte Real
G = real(Ybarra);
% Parte Imaginária
B = imag(Ybarra);

%% RESÍDUOS DE POTÊNCIA

% Tensões em Coordenadas Retangulares
[x,y] = pol2cart(TETA,V); % Teta em radianos
Vret = x+1i*y;

% Correntes injetadas
I = Ybarra*Vret;

% Potência Complexa = Pcalc + j*Qcalc
S = Vret.*conj(I);
Pcalc = real(S);    % Fluxo Ativo Líquido que será enviado para as LTs
Qcalc = imag(S);    % Análogo

% Cálculo dos Resíduos
for k=1:NBAR
    delta_P(k) = Pesp(k) - Pcalc(k);
    delta_Q(k) = Qesp(k) - Qcalc(k);
    
    %Se a barra for do tipo 2 (swing), não tem resíduos
    if(TIPO(k)==2)
        delta_P(k)=0; delta_Q(k)=0;
    end
    
    %Se a barra for do tipo 1 (PV), não tem resíduo de Q
    if(TIPO(k)==1)
        delta_Q(k)=0;
    end
end

% Vetor de Resíduos
delta_Y = [delta_P';delta_Q'];

% Máximo Erro para convergência
MAX_Y = max(abs(delta_Y));

divergente=0; % variável auxiliar para determinar se o processo convergiu ou divergiu

while (MAX_Y > tol)
    %**********************************************************************
    %   MONTAGEM DA MATRIZ JACOBIANA
    %**********************************************************************
    
    %Suprimir mensagem de aviso de singularidade
    %warning('off','MATLAB:singularMatrix');


    for k1=1:NBAR
        for k2=1:NBAR
            if(k1==k2)
                H(k1,k1)=-(Qcalc(k1)+V(k1)^2*B(k1,k1));
                N(k1,k1)=inv(V(k1))*(Pcalc(k1)+V(k1)^2*G(k1,k1));
                M(k1,k1)=Pcalc(k1)-V(k1)^2*G(k1,k1);
                L(k1,k1)=inv(V(k1))*(Qcalc(k1)-V(k1)^2*B(k1,k1));

                %Alterações pelo Tipo de Barra (swing e PV)

                if(TIPO(k1)==2)
                    H(k1,k1)=10^10;
                    L(k1,k1)=10^10;
                end

                if(TIPO(k1)==1)
                    L(k1,k1)=10^10;
                end
            else
                H(k1,k2)=V(k1)*V(k2)*(G(k1,k2)*sin(TETA(k1)-TETA(k2))-B(k1,k2)*cos(TETA(k1)-TETA(k2)));
                N(k1,k2)=V(k1)*(G(k1,k2)*cos(TETA(k1)-TETA(k2))+B(k1,k2)*sin(TETA(k1)-TETA(k2)));
                M(k1,k2)=-V(k1)*V(k2)*(G(k1,k2)*cos(TETA(k1)-TETA(k2))+B(k1,k2)*sin(TETA(k1)-TETA(k2)));
                L(k1,k2)=V(k1)*(G(k1,k2)*sin(TETA(k1)-TETA(k2))-B(k1,k2)*cos(TETA(k1)-TETA(k2)));
            end
        end
    end


    Jac = [H N;M L];

    %**********************************************************************
    %   RESOLUÇÃO DO SISTEMA E ATUALIZAÇÃO
    %**********************************************************************
    
    delta_SOLUCAO = inv(Jac)*delta_Y; %[delta_TETA;delta_V]
    TETA = TETA + delta_SOLUCAO(1:NBAR,1);
    V = V + delta_SOLUCAO((NBAR+1):2*NBAR,1);    
    
    %**********************************************************************
    %   CÁLCULO DOS RESÍDUOS
    %**********************************************************************
    

        % Tensões em Coordenadas Retangulares
        [x,y] = pol2cart(TETA,V); % Teta em radianos
        Vret = x+1i*y;

        % Correntes injetadas
        I = Ybarra*Vret;

        % Potência Complexa = Pcalc + j*Qcalc
        S = Vret.*conj(I);
        Pcalc = real(S);    % Fluxo Ativo Líquido que será enviado para as LTs
        Qcalc = imag(S);    % Análogo

        % Cálculo dos Resíduos
        for k=1:NBAR
            delta_P(k) = Pesp(k) - Pcalc(k);
            delta_Q(k) = Qesp(k) - Qcalc(k);

            %Se a barra for do tipo 2 (swing), não tenho resíduos
            if(TIPO(k)==2)
                delta_P(k)=0; delta_Q(k)=0;
            end

            %Se a barra for do tipo 1 (PV), não tem resíduo de Q
            if(TIPO(k)==1)
                delta_Q(k)=0;
            end
        end

    % Vetor de Resíduos
    delta_Y = [delta_P';delta_Q'];

    % Máximo Erro para convergência
    MAX_Y = max(abs(delta_Y));
    
     % Número de Iterações:
    iteracao = iteracao + 1;
    if((iteracao>25))
        divergente = 1;
        break;
    end

end

%% Cáculo do Fluxo de Potência Ativa
for i=1:NLIN
    K=DE(i);
    M=PARA(i);
    
    FLUXO(i,1)=-(((TAP(i)*V(K))^2)*G(K,M) - (TAP(i)*V(K))*V(M)*G(K,M)*cos(TETA(K)-TETA(M)) - (TAP(i)*V(K))*V(M)*B(K,M)*sin(TETA(K)-TETA(M)))* Pbase;
    FLUXO(i,2)=-(((TAP(i)*V(M))^2)*G(M,K) - (TAP(i)*V(M))*V(K)*G(M,K)*cos(TETA(M)-TETA(K)) - (TAP(i)*V(M))*V(K)*B(M,K)*sin(TETA(M)-TETA(K)))* Pbase;
    
    if(FLUXO(i,1)>FLUXO(i,2))
        FLUXO(i,4)=FLUXO(i,3)-abs(FLUXO(i,1));
        FLUXO(i,5)=abs(FLUXO(i,1));
    else
        FLUXO(i,4)=FLUXO(i,3)-abs(FLUXO(i,2));
        FLUXO(i,5)=abs(FLUXO(i,2));
    end        
end

%% Impressão dos Resultados

%Dados de Barra
if(divergente==1)
    disp('O caso Divergiu');
else
    
    disp('=============================================================================================================');
    disp(sprintf('- Número de Iterações: %d',iteracao));
    disp('=============================================================================================================');
    disp(sprintf('- Resíduo Máximo: %g < Tolerância de %.3f',MAX_Y,tol));
    disp('=============================================================================================================');
    disp(sprintf('- Dados Finais de Barra (pu):\n'));
    disp(sprintf('\tNº\t\t  Tipo\t\tTensão\tAngulo(º)\tPG\t\t  QG\t\tQmín\t  Qmáx\t\tPdemanda  Qdemanda\n'));
    disp([[1:NBAR]',TIPO,V,TETA*180/pi,(Pcalc+PD).*Pbase,(Qcalc+QD).*Pbase,QN.*Pbase,QM.*Pbase,PD.*Pbase,QD.*Pbase]);
    disp('=============================================================================================================');
    

end

%Dados de Linha
disp('=============================================================================================================');
disp('Fluxo de Potência Ativa entre as Barras');
disp('=============================================================================================================');
disp(sprintf('\tDE\t\t  PARA\t  DE-PARA\tPARA-DE\t FLUXO MAX\t FOLGA\n'));
disp([DE,PARA,FLUXO(:,1),FLUXO(:,2),FLUXO(:,3),FLUXO(:,4)]);
disp('=============================================================================================================');