#!/bin/bash
# Solid-only order study on the Hron-Turek flap: 0.35 x 0.02 m, St Venant-
# Kirchhoff, plane strain, E = 1.4 MPa, nu = 0.4, clamped at x = 0, a uniform
# pressure ramped to 20 Pa over 10 load steps on the upper face (tip deflection
# ~ 10% of the length, as in FSI3). Non-polynomial solution, self-convergence.
# p = 1: the tutorial's standard scheme; p = 2, 3, 4: highOrderCoeffs.
# Usage: flap_study.sh <worktree> <outdir> [jobs] [levels...]
set -u
WT=$1; OUT=$2; JOBS=${3:-8}; shift 3; LEVELS=${*:-6 12 24 48}
TUT=$WT/tutorials/solids/linearElasticity/cantilever2d
mkdir -p "$OUT"
make_case() {
    source $HOME/claude-runs/hoStudy/env.sh   # SIP strips DYLD_* in child bash
    local p=$1 n=$2
    local c=$OUT/p${p}_n${n}
    rm -rf "$c"; mkdir -p "$c/0" "$c/constant" "$c/system"
    local suffix=petscSnes; [ "$p" != 1 ] && suffix=highOrder
    cp "$TUT/system/fvSchemes" "$c/system/"
    cp "$WT/tutorials/fluidSolidInteraction/TurekHron2006/system/solid/fvSolution" "$c/system/fvSolution"
    cp "$TUT/constant/dynamicMeshDict" "$TUT/constant/g" "$TUT/constant/physicsProperties" "$c/constant/"
    local nx=$((n*35/2))
    cat > "$c/system/blockMeshDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }
vertices ( (0 0 0) (0.35 0 0) (0.35 0.02 0) (0 0.02 0)
           (0 0 0.015) (0.35 0 0.015) (0.35 0.02 0.015) (0 0.02 0.015) );
blocks ( hex (0 1 2 3 4 5 6 7) ($nx $n 1) simpleGrading (1 1 1) );
boundary
(
    left   { type patch; faces ((0 4 7 3)); }
    right  { type patch; faces ((1 2 6 5)); }
    bottom { type patch; faces ((0 1 5 4)); }
    top    { type patch; faces ((3 7 6 2)); }
    frontAndBack { type empty; faces ((0 3 2 1) (4 5 6 7)); }
);
EOF
    cat > "$c/system/controlDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
libs ("libsolids4FoamModels.so");
application solids4Foam; startFrom startTime; startTime 0; stopAt endTime;
endTime 1; deltaT 0.1; writeControl timeStep; writeInterval 10;
writeFormat ascii; writePrecision 12; timeFormat general; timePrecision 6;
runTimeModifiable no;
functions
{
    tip { type solidPointDisplacement; point (0.35 0.01 0.0075); }
}
EOF
    cat > "$c/constant/timeVsPressure" <<EOF
( (0 0) (1 20) )
EOF
    cat > "$c/constant/mechanicalProperties" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object mechanicalProperties; }
planeStress no;
mechanical ( flap { type StVenantKirchhoffElastic; rho rho [1 -3 0 0 0 0 0] 1000;
    E E [1 -1 -2 0 0 0 0] 1.4e6; nu nu [0 0 0 0 0 0 0] 0.4; } );
EOF
    local ho=""
    if [ "$p" != 1 ]; then ho="
    highOrderCoeffs
    {
        highOrderResidual true;
        highOrderJacobian true;
        displacement
        {
            polynomialOrder $p;
            faceStencilExtraCells 15;
            weightFunctionCoeffs { type radiallySymmetricExponential; k 6; }
            calcConditionNumber false;
        }
    }"; fi
    local stab="diffStencilLaplacian; scaleFactor 0.5"
    [ "$p" != 1 ] && stab="alpha; scaleFactor 0.1"
    cat > "$c/constant/solidProperties" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object solidProperties; }
solidModel nonLinearGeometryTotalLagrangianTotalDisplacement;
nonLinearGeometryTotalLagrangianTotalDisplacementCoeffs
{
    solutionAlgorithm PETScSNES;
    predictor no;$ho
    stabilisation { momentum { type $stab; } }
}
EOF
    cat > "$c/0/D" <<EOF
FoamFile { version 2.0; format ascii; class volVectorField; object D; }
dimensions [0 1 0 0 0 0 0];
internalField uniform (0 0 0);
boundaryField
{
    left   { type fixedDisplacement; value uniform (0 0 0); }
    right  { type solidTraction; traction uniform (0 0 0); pressure uniform 0; value uniform (0 0 0); }
    bottom { type solidTraction; traction uniform (0 0 0); pressure uniform 0; value uniform (0 0 0); }
    top
    {
        type solidTraction; traction uniform (0 0 0);
        pressureSeries { file "\$FOAM_CASE/constant/timeVsPressure"; outOfBounds clamp; }
        value uniform (0 0 0);
    }
    frontAndBack { type empty; }
}
EOF
    cd "$c" && blockMesh > log.blockMesh 2>&1 && solids4Foam > log.solids4Foam 2>&1
    echo "p=$p n=$n rc=$? $(tail -1 postProcessing/0/solidPointDisplacement_tip.dat 2>/dev/null)"
}
export -f make_case; export OUT TUT WT
for n in $LEVELS; do for p in 1 2 3; do echo "$p $n"; done; done | \
    xargs -P "$JOBS" -n 2 bash -c 'make_case "$0" "$1"'
