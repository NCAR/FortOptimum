      PROGRAM Grad_Term_GPU
      
      IMPLICIT NONE

      INTEGER, PARAMETER :: DOUBLE=SELECTED_REAL_KIND(p=14,r=100)

      INTEGER, PARAMETER :: nx=4      ! element order
      INTEGER, PARAMETER :: npts=nx*nx
      INTEGER, PARAMETER :: nit=10   ! iteration count
      INTEGER, PARAMETER :: nelem=6*120*120

      REAL(KIND=DOUBLE), PARAMETER :: dt=.005D0 ! fake timestep

      REAL(KIND=DOUBLE) :: der(nx,nx)   ! Derivative matrix
      REAL(KIND=DOUBLE) :: delta(nx,nx) ! Kronecker delta function
      REAL(KIND=DOUBLE) :: gw(nx)       ! Gaussian wts
      REAL(KIND=DOUBLE), DIMENSION(nx*nx,nelem) :: flx,fly
      REAL(KIND=DOUBLE), DIMENSION(nx*nx,nelem) :: grad     

      REAL(KIND=DOUBLE) :: s1, s2
      INTEGER(KIND=8) :: count1, count_rate1, count_max
      INTEGER(KIND=8) :: count2, count_rate2

      INTEGER :: i, j, k, l, ii, ie, it

      ! Init static matrices

      der(:,:)=1.0_8
      gw(:) = 0.5_8

      delta(:,:)=0.0_8
      delta(1,1)=1.0_8
      delta(2,2)=1.0_8

      ! Load up some initial values

      flx(:,:) = 1.0_8
      fly(:,:) = -1.0_8

      CALL SYSTEM_CLOCK(count1, count_rate1, count_max)

      DO it=1,nit
      DO ie=1,nelem
         DO ii=1,npts
            k=MODULO(ii-1,nx)+1
            l=(ii-1)/nx+1
            s2 = 0.0_8
            DO j = 1, nx
               s1 = 0.0_8
               DO i = 1, nx
                  s1 = s1 + (delta(l,j)*flx(i+(j-1)*nx,ie)*der(i,k) + &
                             delta(i,k)*fly(i+(j-1)*nx,ie)*der(j,l))*gw(i)
               END DO  ! i loop
               s2 = s2 + s1*gw(j) 
            END DO ! j loop
            grad(ii,ie) = s2
         END DO ! i1 loop
      END DO ! ie

     !write(*,*) "Done with gradient"

      DO ie=1,nelem
         DO ii=1,npts
            flx(ii,ie) = flx(ii,ie)+ dt*grad(ii,ie)
            fly(ii,ie) = fly(ii,ie)+ dt*grad(ii,ie)
         END DO
      END DO
      
      END DO ! iteration count, it

      CALL SYSTEM_CLOCK(count2, count_rate2, count_max)

      WRITE(*, *) "****************** RESULT ********************"
      WRITE(*, *)
      WRITE(*, "(A,I2,A,I2,A)") "DG_KERNEL VERSION (",0," ,",0," )"
      WRITE(*, *)
      WRITE(*, "(A, I1,A,I2,A,I10,A,I8)")  "TARGET = ",0,", NX = ",4,", NELEM = ",6*120*120,", NIT = ", nit
      WRITE(*, "(A,E15.7)") "MAX(flx) = ", MAXVAL(flx)
      WRITE(*, "(A,E15.7)") "MIN(fly) = ", MINVAL(fly)
      WRITE(*,*) "CLOCK START", count1, count_rate1
      WRITE(*,*) "CLOCK STOP", count2, count_rate2

      END PROGRAM Grad_Term_GPU
