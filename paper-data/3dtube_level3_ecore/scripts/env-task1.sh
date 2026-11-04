# Environment for the paper-fsi-verification Task 1 (3dTube) runs
# Usage:  source ~/OpenFOAM/balis-v2512/env-task1.sh
source /opt/openfoam/OpenFOAM-v2512/etc/bashrc
export PETSC_DIR=/opt/openfoam/ThirdParty-v2512/platforms/linux64GccDPInt32/petsc-3.21.2
export PETSC_ARCH=
export LD_LIBRARY_PATH=$PETSC_DIR/lib:$LD_LIBRARY_PATH
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
