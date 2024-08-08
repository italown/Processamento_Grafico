#ifndef BEZIERHEADER
#define BEZIERHEADER

#include <vector>
#include <map>

#include "Object.cpp"
#include "Vector.cpp"
#include "Point.cpp"
#include "Ray.cpp"
#include "Triangle.cpp"

long long int fatorial(int n){
    if (n==1 || n==0){
        return 1;
    }
    return fatorial(n - 1) * n;
}

class Bezier : public object {
    private:
        vector<vector<vetor>> controlPoints;
        std::vector<object*> triangles;
        vetor kd;  // Difuso
        vetor ks;  // Specular
        vetor ke;  // Emissivo
        vetor ka;  // Ambiente
        double ns; // Brilho
        double ni; // Índice de refração
        double d;  // Opacidade
        ray* ra;
    public:

        Bezier(std::vector<std::vector<vetor>> controlPoints,
            vetor color,
            vetor kd,
            vetor ks,
            vetor ke,
            vetor ka,
            double ns,
            double ni,
            double d)

            : object(color),
            controlPoints(controlPoints),
            kd(kd),
            ks(ks),
            ke(ke),
            ka(ka),
            ns(ns),
            ni(ni),
            d(d) {}

        ~Bezier() {}

        vetor getColor() {
            return this->kd;
        }

        double intersect (ray &r) override {}


        double bernstein(int n, int i, double t) {
            long long int binomial_coef = fatorial(n) / (fatorial(i) * fatorial(n - i));
            return binomial_coef * pow(t, i) * (pow(1 - t, n - i));
        }

        point surface_point(double s, double t){
            int rows = controlPoints.size();
            vetor p = vetor(0,0,0);
            int columns;
            double bs;
            double bt;

            for(int i=0; i<rows; i++){
                columns = controlPoints[i].size();
                for(int j=0; j<columns; j++){
                    bs = bernstein(rows - 1, i, s);
                    bt = bernstein(columns - 1, j, t);
                    p = p + (bs * bt * controlPoints[i][j]);
                } 
            }

            point ponto = point(p.getX(), p.getY(), p.getZ());
            return ponto;
        }

    std::vector<object*> triangulate(double tolerance) {
        vector<point> bezier_points;
        vector<vector<int>> listTriangles;

        int steps = static_cast<int>(1.0 / tolerance) + 1; // Ajuste para incluir os pontos finais

        for (int i = 0; i < steps; i++) {
            for (int j = 0; j < steps; j++) {
                double s = i * tolerance;
                double t = j * tolerance;
                bezier_points.push_back(surface_point(s, t));
            }
        }

        int n = steps - 1; // Ajuste para refletir o número real de segmentos

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                int top_left = i * steps + j;
                int top_right = top_left + 1;
                int bottom_left = top_left + steps;
                int bottom_right = bottom_left + 1;

                listTriangles.push_back({top_left, bottom_left, top_right});
                listTriangles.push_back({bottom_left, bottom_right, top_right});
            }
        }

        for (int i = 0; i < listTriangles.size(); i++) {
            int idxA = listTriangles[i][0];
            int idxB = listTriangles[i][1];
            int idxC = listTriangles[i][2];
            
            if (idxA >= bezier_points.size() || idxB >= bezier_points.size() || idxC >= bezier_points.size()) {
                continue; // Ignorar triângulos fora dos limites
            }
            
            point A = bezier_points[idxA];
            point B = bezier_points[idxB];
            point C = bezier_points[idxC];
            vetor v = vetor(1, 1, 1);
            triangle* newTriangle = new triangle(v, 
                A, B, C, 
                this->kd, 
                this->ks, 
                this->ke, 
                this->ka, 
                this->ns, 
                this->ni, 
                this->d
        );
        triangles.push_back(newTriangle);
    }
            return this->triangles;
        }

        //GETTERS
        double getD() override { return d; }
        double getShininess() override { return ns; }
        double getNi() override { return ni; }
        vetor getKd() override { return kd; }
        vetor getKs() override { return ks; }
        vetor getKe() override { return ke; }
        vetor getKa() override { return ka; }
        std::vector<std::vector<vetor>> getControlPoints() { return controlPoints; }
        std::vector<object*> getTriangles() { return triangles; }

        point getPonto() override{};
        vetor getNormal() override{};
        void rotacao(double angle, char eixo, point centroide){};
        void translacao(double dx, double dy, double dz){};
        void cisalhamento(double shXY, double shXZ, double shYX, double shYZ, double shZX, double shZY){};
};

#endif