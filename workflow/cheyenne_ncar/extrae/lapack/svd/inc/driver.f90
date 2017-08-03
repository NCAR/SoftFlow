
module EXTRAE_MODULE
    interface
        subroutine extrae_user_function (enter)
            integer*4, intent(in) :: enter
        end subroutine extrae_user_function
        subroutine extrae_next_hwc_set
        end subroutine extrae_next_hwc_set
    end interface
end module EXTRAE_MODULE

       MODULE SVDDRIVER

           PUBLIC DRIVER

       CONTAINS

           SUBROUTINE DRIVER()

               INTEGER, PARAMETER :: REP=3
               INTEGER, PARAMETER :: MAXRUN=10
               INTEGER, PARAMETER :: BASE=64
               INTEGER, PARAMETER :: M=BASE+MAXRUN*8, N=BASE+MAXRUN*4
               DOUBLE PRECISION A(M,N),U(M,M),S(N),V(N,N)
               INTEGER :: L1, L2, K, I, J, LWORK
               DOUBLE PRECISION,ALLOCATABLE :: WORK(:)

              LWORK=MAX(1,3*MIN(M,N)+MAX(M,N),5*MIN(M,N))

              ALLOCATE(work(lwork))


            DO L1=1, REP
               DO L2=1, MAXRUN
                   K=1
                   DO I=1,BASE+L2*8
                    DO J=1,BASE+L2*4
                       A(I,J)=K*1.0D0
                       K=K+1
                     END DO
                   END DO

                   CALL SVDTEST(A,U,S,V,BASE+L2*8,BASE+L2*4, LWORK, WORK)
                   
                !U = 0
                !S = 0
                !V = 0
               END DO
           END DO

!               WRITE(*,*) 'U ='
!               WRITE(*,'(4F10.4)') ((U(I,J),J=1,M),I=1,M)
!               WRITE(*,*) 'V='
!               WRITE(*,'(2F10.4)') V
               WRITE(*,*) 'S =' 
               WRITE(*,'(2F20.4)')S

           END SUBROUTINE


           SUBROUTINE SVDTEST(A,U,S,V,M,N,LWORK,WORK)
              DOUBLE PRECISION A(M,N),U(M,M),VT(N,N),S(N),V(N,N)

              !DOUBLE PRECISION,ALLOCATABLE :: WORK(:)
              DOUBLE PRECISION :: WORK(:)
              INTEGER LDA,M,N,LWORK,LDVT,INFO
              CHARACTER  JOBU, JOBVT

              EXTERNAL DGESVD

              JOBU='A'
              JOBVT='A'
              LDA=M
              LDU=M
              LDVT=N

              !LWORK=MAX(1,3*MIN(M,N)+MAX(M,N),5*MIN(M,N))

              !ALLOCATE(work(lwork))

        call extrae_user_function (1)

              CALL DGESVD(JOBU, JOBVT, M, N, A, LDA, S, U, LDU, VT, LDVT, WORK, LWORK, INFO )

        call extrae_user_function (0)
        call extrae_next_hwc_set

               DO I=1,2
                 DO J=1,2
                   V(J,I)=VT(I,J)
                 END DO
               END DO
           END
       END MODULE
