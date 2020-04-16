!                    ************************
                     SUBROUTINE USER_CONDIN_H
!                    ************************
!
!
!***********************************************************************
! TELEMAC2D   V7P3
!***********************************************************************
!
!brief    USER INITIALISES THE PHYSICAL PARAMETERS U, V
!
!history  J-M HERVOUET (LNHE)
!+        30/08/2007
!+        V6P0
!+
!
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!
      USE BIEF
      USE DECLARATIONS_TELEMAC
      USE DECLARATIONS_TELEMAC2D
      USE TPXO
      USE OKADA
!
      USE DECLARATIONS_SPECIAL
      IMPLICIT NONE
!
!+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
!
      INTEGER I, J
      INTEGER NA
      INTEGER IERR
!
      DOUBLE PRECISION TEMP, WEIGHT1, WEIGHT2
      DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: SUBX
      DOUBLE PRECISION, DIMENSION(:), ALLOCATABLE :: EXACTH, EXACTU
!
!-----------------------------------------------------------------------
!
!     TESTING IF ANALYTICAL SOLUTION FILE EXISTS
      OPEN(20, FILE='../ANALYTIC_SOL.txt', IOSTAT=IERR)
      IF (IERR/=0) THEN
        WRITE(*, *) "UNABLE TO READ ANALYTIC SOLUTION FILE"
        STOP
      ENDIF
!
!     COMPUTING NUMBER OF LINES IN ANALYTIC SOLUTION FILE
      NA = 0
      DO WHILE (IERR==0)
        READ(20, '(A)', IOSTAT=IERR)
        IF (IERR==0) THEN
          NA = NA + 1
        ENDIF
      ENDDO
      CLOSE(20)
!
      ALLOCATE(SUBX(NA))
      ALLOCATE(EXACTH(NA))
      ALLOCATE(EXACTU(NA))
!
!     READING ANALYTIC SOLUTION
      OPEN(20, FILE='../ANALYTIC_SOL.txt')
      DO I=1,NA
        READ(20, *) SUBX(I), EXACTH(I), EXACTU(I)
      ENDDO
      CLOSE(20)
!
!     INITIALISATION OF H, U, V
      DO I=1,NA-1
        DO J=1,NPOIN
          IF ((SUBX(I).LE.X(J)).AND.(X(J).LE.SUBX(I+1))) THEN
            TEMP = SUBX(I+1) - SUBX(I)
            WEIGHT1 = (SUBX(I+1) - X(J))/TEMP
            WEIGHT2 = (X(J) - SUBX(I))/TEMP
            H%R(J) = WEIGHT1*EXACTH(I) + WEIGHT2*EXACTH(I+1)
            U%R(J) = WEIGHT1*EXACTU(I) + WEIGHT2*EXACTU(I+1)
            V%R(J) = 0.0D0
          ENDIF
        ENDDO
      ENDDO
!
!-----------------------------------------------------------------------
!
      DEALLOCATE(SUBX)
      DEALLOCATE(EXACTH)
      DEALLOCATE(EXACTU)
!
      RETURN
      END
