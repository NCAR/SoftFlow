! This code is part of
! RRTM for GCM Applications - Parallel (RRTMGP)
!
! Eli Mlawer and Robert Pincus
! Andre Wehe and Jennifer Delamere
! email:  rrtmgp@aer.com
!
! Copyright 2015-2016,  Atmospheric and Environmental Research and
! Regents of the University of Colorado.  All right reserved.
!
! Use and duplication is permitted under the terms of the
!    BSD 3-clause license, see http://opensource.org/licenses/BSD-3-Clause
!
! Description:  Addition of optical properties -- the first set are incremented by the second set. 
!   There are three possible representations of optical properties (scalar = optical depth only; 
!   two-stream = tau, single-scattering albedo, and asymmetry factor g, and 
!   n-stream = tau, ssa, and phase function moments p.) Thus we need nine routines, three for 
!   each choice of representation on the left hand side times three representations of the 
!   optical properties to be added. 
!   There are two sets of these nine routines. In the first the two sets of optical 
!   properties are defined at the same spectral resolution. There is also a set of routines
!   to add properties defined at lower spectral resolution to a set defined at higher spectral 
!   resolution (adding properties defined by band to those defined by g-point) 

module mo_optical_props_kernels
  use mo_rrtmgp_kind, only: wp
  implicit none 
  public 
contains 
  ! ---------------------------------
  ! ---------------------------------
  pure subroutine increment_1scalar_by_1scalar(ncol, nlay, ngpt, &  
                                               tau1,             & 
                                               tau2)
    integer,                              intent(in  ) :: ncol, nlay, ngpt
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1
    real(wp), dimension(ncol,nlay,ngpt), intent(in   ) :: tau2

    integer  :: icol, ilay, igpt
    
    do igpt = 1, ngpt
      do ilay = 1, nlay
        do icol = 1, ncol
          tau1(icol,ilay,igpt) = tau1(icol,ilay,igpt) + tau2(icol,ilay,igpt)
        end do
      end do
    end do
  end subroutine increment_1scalar_by_1scalar
  ! ---------------------------------
  ! increment 1scalar by 2stream
  pure subroutine increment_1scalar_by_2stream(ncol, nlay, ngpt, &  
                                               tau1,             & 
                                               tau2, ssa2)
    integer,                              intent(in   ) :: ncol, nlay, ngpt
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1
    real(wp), dimension(ncol,nlay,ngpt), intent(in   ) :: tau2, ssa2

    integer  :: icol, ilay, igpt
    
    do igpt = 1, ngpt
      do ilay = 1, nlay
        do icol = 1, ncol
          tau1(icol,ilay,igpt) = tau1(icol,ilay,igpt) + & 
                                 tau2(icol,ilay,igpt) * (1._wp - ssa2(icol,ilay,igpt))
        end do
      end do
    end do
  end subroutine increment_1scalar_by_2stream
  ! ---------------------------------
  ! increment 1scalar by nstream
  pure subroutine increment_1scalar_by_nstream(ncol, nlay, ngpt, &  
                                               tau1,             & 
                                               tau2, ssa2)
    integer,                              intent(in   ) :: ncol, nlay, ngpt
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1
    real(wp), dimension(ncol,nlay,ngpt), intent(in   ) :: tau2, ssa2

    integer  :: icol, ilay, igpt
    
    do igpt = 1, ngpt
      do ilay = 1, nlay
        do icol = 1, ncol
          tau1(icol,ilay,igpt) = tau1(icol,ilay,igpt) + & 
                                 tau2(icol,ilay,igpt) * (1._wp - ssa2(icol,ilay,igpt))
        end do
      end do
    end do
  end subroutine increment_1scalar_by_nstream
  ! ---------------------------------
  ! ---------------------------------
  ! increment 2stream by 1scalar
  pure subroutine increment_2stream_by_1scalar(ncol, nlay, ngpt, &  
                                               tau1, ssa1,       & 
                                               tau2)
    integer,                              intent(in   ) :: ncol, nlay, ngpt
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1
    real(wp), dimension(ncol,nlay,ngpt), intent(in   ) :: tau2

    integer  :: icol, ilay, igpt
    real(wp) :: tau12 
    
    do igpt = 1, ngpt
      do ilay = 1, nlay
        do icol = 1, ncol
          tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,igpt)
          ssa1(icol,ilay,igpt) = tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) / tau12
          tau1(icol,ilay,igpt) = tau12
          ! g is unchanged 
        end do
      end do
    end do
  end subroutine increment_2stream_by_1scalar
  ! ---------------------------------
  ! increment 2stream by 2stream
  pure subroutine increment_2stream_by_2stream(ncol, nlay, ngpt, &  
                                               tau1, ssa1, g1,   & 
                                               tau2, ssa2, g2)
    integer,                              intent(in   ) :: ncol, nlay, ngpt
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1, g1
    real(wp), dimension(ncol,nlay,ngpt), intent(in   ) :: tau2, ssa2, g2

    integer :: icol, ilay, igpt
    real(wp) :: tau12, tauscat12

    do igpt = 1, ngpt
      do ilay = 1, nlay
        do icol = 1, ncol
          ! t=tau1 + tau2
          tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,igpt)
          ! w=(tau1*ssa1 + tau2*ssa2) / t
          tauscat12 = & 
             tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) + & 
             tau2(icol,ilay,igpt) * ssa2(icol,ilay,igpt)
          g1(icol,ilay,igpt) = & 
            (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * g1(icol,ilay,igpt) + & 
             tau2(icol,ilay,igpt) * ssa2(icol,ilay,igpt) * g2(icol,ilay,igpt)) / tauscat12
          ssa1(icol,ilay,igpt) = tauscat12 / tau12
          tau1(icol,ilay,igpt) = tau12
        end do
      end do
    end do
  end subroutine increment_2stream_by_2stream
  ! ---------------------------------
  ! increment 2stream by nstream
  pure subroutine increment_2stream_by_nstream(ncol, nlay, ngpt, nmom2, &  
                                               tau1, ssa1, g1,          & 
                                               tau2, ssa2, p2)
    integer,                              intent(in   ) :: ncol, nlay, ngpt, nmom2
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1, g1
    real(wp), dimension(ncol,nlay,ngpt), intent(in   ) :: tau2, ssa2
    real(wp), dimension(nmom2, &  
                        ncol,nlay,ngpt), intent(in   ) :: p2

    integer  :: icol, ilay, igpt
    real(wp) :: tau12, tauscat12

    do igpt = 1, ngpt
      do ilay = 1, nlay
        do icol = 1, ncol
          ! t=tau1 + tau2
          tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,igpt)
          ! w=(tau1*ssa1 + tau2*ssa2) / t
          tauscat12 = & 
             tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) + & 
             tau2(icol,ilay,igpt) * ssa2(icol,ilay,igpt)
          g1(icol,ilay,igpt) = & 
            (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * g1(   icol,ilay,igpt)+ & 
             tau2(icol,ilay,igpt) * ssa2(icol,ilay,igpt) * p2(1, icol,ilay,igpt)) / tauscat12
          ssa1(icol,ilay,igpt) = tauscat12 / tau12
          tau1(icol,ilay,igpt) = tau12
        end do
      end do
    end do
  end subroutine increment_2stream_by_nstream
  ! ---------------------------------
  ! ---------------------------------
  ! increment nstream by 1scalar
  pure subroutine increment_nstream_by_1scalar(ncol, nlay, ngpt, &  
                                               tau1, ssa1,       & 
                                               tau2)
    integer,                              intent(in   ) :: ncol, nlay, ngpt
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1
    real(wp), dimension(ncol,nlay,ngpt), intent(in   ) :: tau2

    integer  :: icol, ilay, igpt
    real(wp) :: tau12 
    
    do igpt = 1, ngpt
      do ilay = 1, nlay
        do icol = 1, ncol
          tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,igpt)
          ssa1(icol,ilay,igpt) = tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) / tau12
          tau1(icol,ilay,igpt) = tau12
          ! p is unchanged 
        end do
      end do
    end do
  end subroutine increment_nstream_by_1scalar
  ! ---------------------------------
  ! increment nstream by 2stream
  pure subroutine increment_nstream_by_2stream(ncol, nlay, ngpt, nmom1, & 
                                               tau1, ssa1, p1,          & 
                                               tau2, ssa2, g2)
    integer,                              intent(in   ) :: ncol, nlay, ngpt, nmom1 
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1
    real(wp), dimension(nmom1, &  
                        ncol,nlay,ngpt), intent(inout) :: p1
    real(wp), dimension(ncol,nlay,ngpt), intent(in   ) :: tau2, ssa2, g2

    integer  :: icol, ilay, igpt
    real(wp) :: tau12, tauscat12
    real(wp), dimension(nmom1) :: temp_moms ! TK 
    integer  :: imom  !TK 

    do igpt = 1, ngpt
      do ilay = 1, nlay
        do icol = 1, ncol
          tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,igpt)
          tauscat12 = & 
             tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) + & 
             tau2(icol,ilay,igpt) * ssa2(icol,ilay,igpt)
          !
          ! Here assume Henyey-Greenstein 
          !
          temp_moms(1) = g2(icol,ilay,igpt)
          do imom = 2, nmom1
            temp_moms(imom) = temp_moms(imom-1) * g2(icol,ilay,igpt)
          end do           
          p1(2:nmom1, icol,ilay,igpt) = & 
              (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * p1(2:nmom1, icol,ilay,igpt) + & 
               tau2(icol,ilay,igpt) * ssa2(icol,ilay,igpt) * temp_moms(2:nmom1)  ) / tauscat12
          !
          ! Assume all moments of two-stream phase function beyond first moment are 0. 
          !
          p1(1, icol,ilay,igpt) = & 
              (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * p1(1, icol,ilay,igpt) + & 
               tau2(icol,ilay,igpt) * ssa2(icol,ilay,igpt) * g2(   icol,ilay,igpt)) / tauscat12

          ssa1(icol,ilay,igpt) = tauscat12 / tau12
          tau1(icol,ilay,igpt) = tau12
        end do
      end do
    end do
  end subroutine increment_nstream_by_2stream
  ! ---------------------------------
  ! increment nstream by nstream
  pure subroutine increment_nstream_by_nstream(ncol, nlay, ngpt, nmom1, nmom2, & 
                                               tau1, ssa1, p1,                 & 
                                               tau2, ssa2, p2)
    integer,                              intent(in   ) :: ncol, nlay, ngpt, nmom1, nmom2
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1
    real(wp), dimension(nmom1, &  
                        ncol,nlay,ngpt), intent(inout) :: p1
    real(wp), dimension(ncol,nlay,ngpt), intent(in   ) :: tau2, ssa2
    real(wp), dimension(nmom2, &  
                        ncol,nlay,ngpt), intent(in   ) :: p2

    integer  :: icol, ilay, igpt, mom_lim
    real(wp) :: tau12, tauscat12

    mom_lim = min(nmom1, nmom2)
    do igpt = 1, ngpt
      do ilay = 1, nlay
        do icol = 1, ncol
          tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,igpt)
          tauscat12 = & 
             tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) + & 
             tau2(icol,ilay,igpt) * ssa2(icol,ilay,igpt)
          !
          ! If op2 has more moments than op1 these are ignored;
          !   if it has fewer moments the higher orders are assumed to be 0 
          ! 
          p1(1:mom_lim, icol,ilay,igpt) = & 
              (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * p1(1:mom_lim, icol,ilay,igpt) + & 
               tau2(icol,ilay,igpt) * ssa2(icol,ilay,igpt) * p2(1:mom_lim, icol,ilay,igpt)) / tauscat12
          ssa1(icol,ilay,igpt) = tauscat12 / tau12
          tau1(icol,ilay,igpt) = tau12
        end do
      end do
    end do
  end subroutine increment_nstream_by_nstream
  ! ---------------------------------
  !
  ! Incrementing when the second set of optical properties is defined at lower spectral resolution 
  !   (e.g. by band instead of by gpoint) 
  !
  ! ---------------------------------
  pure subroutine inc_1scalar_by_1scalar_bybnd(ncol, nlay, ngpt, &  
                                               tau1,             & 
                                               tau2,             & 
                                               nbnd, gpt_lims)
    integer,                             intent(in   ) :: ncol, nlay, ngpt, nbnd
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1
    real(wp), dimension(ncol,nlay,nbnd), intent(in   ) :: tau2
    integer,  dimension(2,nbnd),         intent(in   ) :: gpt_lims ! Starting and ending gpoint for each band 

    integer :: ibnd, igpt 
    
    do ibnd = 1, nbnd 
      do igpt = gpt_lims(1, ibnd), gpt_lims(2, ibnd)
        tau1(:,:,igpt) = tau1(:,:,igpt) + tau2(:,:,ibnd)
      end do 
    end do 
  end subroutine inc_1scalar_by_1scalar_bybnd
  ! ---------------------------------
  ! increment 1scalar by 2stream
  pure subroutine inc_1scalar_by_2stream_bybnd(ncol, nlay, ngpt, &  
                                               tau1,             & 
                                               tau2, ssa2,       & 
                                               nbnd, gpt_lims)
    integer,                             intent(in   ) :: ncol, nlay, ngpt, nbnd
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1
    real(wp), dimension(ncol,nlay,nbnd), intent(in   ) :: tau2, ssa2
    integer,  dimension(2,nbnd),         intent(in   ) :: gpt_lims ! Starting and ending gpoint for each band 

    integer :: ibnd, igpt 

    do ibnd = 1, nbnd 
      do igpt = gpt_lims(1, ibnd), gpt_lims(2, ibnd)
        tau1(:,:,igpt) = tau1(:,:,igpt) + tau2(:,:,ibnd) * (1._wp - ssa2(:,:,ibnd))
      end do 
    end do 
  end subroutine inc_1scalar_by_2stream_bybnd
  ! ---------------------------------
  ! increment 1scalar by nstream
  pure subroutine inc_1scalar_by_nstream_bybnd(ncol, nlay, ngpt, &  
                                               tau1,             & 
                                               tau2, ssa2,       & 
                                               nbnd, gpt_lims)
    integer,                             intent(in   ) :: ncol, nlay, ngpt, nbnd
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1
    real(wp), dimension(ncol,nlay,nbnd), intent(in   ) :: tau2, ssa2
    integer,  dimension(2,nbnd),         intent(in   ) :: gpt_lims ! Starting and ending gpoint for each band 

    integer :: ibnd, igpt 

    do ibnd = 1, nbnd 
      do igpt = gpt_lims(1, ibnd), gpt_lims(2, ibnd)
        tau1(:,:,igpt) = tau1(:,:,igpt) + tau2(:,:,ibnd) * (1._wp - ssa2(:,:,ibnd))
      end do 
    end do 
  end subroutine inc_1scalar_by_nstream_bybnd
  
    ! ---------------------------------
  ! increment 2stream by 1scalar
  pure subroutine inc_2stream_by_1scalar_bybnd(ncol, nlay, ngpt, &  
                                               tau1, ssa1,       & 
                                               tau2,             &
                                               nbnd, gpt_lims)
    integer,                             intent(in   ) :: ncol, nlay, ngpt, nbnd
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1
    real(wp), dimension(ncol,nlay,nbnd), intent(in   ) :: tau2
    integer,  dimension(2,nbnd),         intent(in   ) :: gpt_lims ! Starting and ending gpoint for each band 

    integer  :: icol, ilay, igpt, ibnd
    real(wp) :: tau12 
    
    do ibnd = 1, nbnd 
      do igpt = gpt_lims(1, ibnd), gpt_lims(2, ibnd)
        do ilay = 1, nlay
          do icol = 1, ncol
            tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,ibnd)
            ssa1(icol,ilay,igpt) = tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) / tau12
            tau1(icol,ilay,igpt) = tau12
            ! g is unchanged 
          end do
        end do
      end do
    end do
  end subroutine inc_2stream_by_1scalar_bybnd
  ! ---------------------------------
  ! increment 2stream by 2stream
  pure subroutine inc_2stream_by_2stream_bybnd(ncol, nlay, ngpt, &  
                                               tau1, ssa1, g1,   & 
                                               tau2, ssa2, g2,   & 
                                               nbnd, gpt_lims)
    integer,                             intent(in   ) :: ncol, nlay, ngpt, nbnd
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1, g1
    real(wp), dimension(ncol,nlay,nbnd), intent(in   ) :: tau2, ssa2, g2
    integer,  dimension(2,nbnd),         intent(in   ) :: gpt_lims ! Starting and ending gpoint for each band 

    integer  :: icol, ilay, igpt, ibnd
    real(wp) :: tau12, tauscat12

    do ibnd = 1, nbnd 
      do igpt = gpt_lims(1, ibnd), gpt_lims(2, ibnd)
        do ilay = 1, nlay
          do icol = 1, ncol
            ! t=tau1 + tau2
            tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,ibnd)
            ! w=(tau1*ssa1 + tau2*ssa2) / t
            tauscat12 = & 
               tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) + & 
               tau2(icol,ilay,ibnd) * ssa2(icol,ilay,ibnd)
            g1(icol,ilay,igpt) = & 
              (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * g1(icol,ilay,igpt) + & 
               tau2(icol,ilay,ibnd) * ssa2(icol,ilay,ibnd) * g2(icol,ilay,ibnd)) / tauscat12
            ssa1(icol,ilay,igpt) = tauscat12 / tau12
            tau1(icol,ilay,igpt) = tau12
          end do
        end do
      end do
    end do
  end subroutine inc_2stream_by_2stream_bybnd
  ! ---------------------------------
  ! increment 2stream by nstream
  pure subroutine inc_2stream_by_nstream_bybnd(ncol, nlay, ngpt, nmom2, &  
                                               tau1, ssa1, g1,          & 
                                               tau2, ssa2, p2,          & 
                                               nbnd, gpt_lims)
    integer,                             intent(in   ) :: ncol, nlay, ngpt, nmom2, nbnd
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1, g1
    real(wp), dimension(ncol,nlay,nbnd), intent(in   ) :: tau2, ssa2
    real(wp), dimension(nmom2, &  
                        ncol,nlay,nbnd), intent(in   ) :: p2
    integer,  dimension(2,nbnd),         intent(in   ) :: gpt_lims ! Starting and ending gpoint for each band 

    integer  :: icol, ilay, igpt, ibnd
    real(wp) :: tau12, tauscat12

    do ibnd = 1, nbnd 
      do igpt = gpt_lims(1, ibnd), gpt_lims(2, ibnd)
        do ilay = 1, nlay
          do icol = 1, ncol
            ! t=tau1 + tau2
            tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,ibnd)
            ! w=(tau1*ssa1 + tau2*ssa2) / t
            tauscat12 = & 
               tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) + & 
               tau2(icol,ilay,ibnd) * ssa2(icol,ilay,ibnd)
            g1(icol,ilay,igpt) = & 
              (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * g1(   icol,ilay,igpt)+ & 
               tau2(icol,ilay,ibnd) * ssa2(icol,ilay,ibnd) * p2(1, icol,ilay,ibnd)) / tauscat12
            ssa1(icol,ilay,igpt) = tauscat12 / tau12
            tau1(icol,ilay,igpt) = tau12
          end do
        end do 
      end do
    end do
  end subroutine inc_2stream_by_nstream_bybnd
  ! ---------------------------------
  ! ---------------------------------
  ! increment nstream by 1scalar
  pure subroutine inc_nstream_by_1scalar_bybnd(ncol, nlay, ngpt, &  
                                               tau1, ssa1,       & 
                                               tau2,             & 
                                               nbnd, gpt_lims)
    integer,                             intent(in   ) :: ncol, nlay, ngpt, nbnd
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1
    real(wp), dimension(ncol,nlay,nbnd), intent(in   ) :: tau2
    integer,  dimension(2,nbnd),         intent(in   ) :: gpt_lims ! Starting and ending gpoint for each band 

    integer  :: icol, ilay, igpt, ibnd
    real(wp) :: tau12 
    
    do ibnd = 1, nbnd 
      do igpt = gpt_lims(1, ibnd), gpt_lims(2, ibnd)
        do ilay = 1, nlay
          do icol = 1, ncol
            tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,ibnd)
            ssa1(icol,ilay,igpt) = tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) / tau12
            tau1(icol,ilay,igpt) = tau12
            ! p is unchanged 
          end do
        end do
      end do 
    end do
  end subroutine inc_nstream_by_1scalar_bybnd
 ! ---------------------------------
  ! increment nstream by 2stream
  pure subroutine inc_nstream_by_2stream_bybnd(ncol, nlay, ngpt, nmom1, & 
                                               tau1, ssa1, p1,          & 
                                               tau2, ssa2, g2,          &
                                               nbnd, gpt_lims)
    integer,                             intent(in   ) :: ncol, nlay, ngpt, nmom1, nbnd
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1
    real(wp), dimension(nmom1, &  
                        ncol,nlay,ngpt), intent(inout) :: p1
    real(wp), dimension(ncol,nlay,nbnd), intent(in   ) :: tau2, ssa2, g2
    integer,  dimension(2,nbnd),         intent(in   ) :: gpt_lims ! Starting and ending gpoint for each band 

    integer  :: icol, ilay, igpt, ibnd
    real(wp) :: tau12, tauscat12
    real(wp), dimension(nmom1) :: temp_moms ! TK 
    integer  :: imom  !TK 

    do ibnd = 1, nbnd 
      do igpt = gpt_lims(1, ibnd), gpt_lims(2, ibnd)
        do ilay = 1, nlay
          do icol = 1, ncol
            tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,ibnd)
            tauscat12 = & 
               tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) + & 
               tau2(icol,ilay,ibnd) * ssa2(icol,ilay,ibnd)
            !
            ! Here assume Henyey-Greenstein 
            !
            temp_moms(1) = g2(icol,ilay,ibnd)
            do imom = 2, nmom1
              temp_moms(imom) = temp_moms(imom-1) * g2(icol,ilay,ibnd)
            end do           
            p1(2:nmom1, icol,ilay,igpt) = & 
                (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * p1(2:nmom1, icol,ilay,igpt) + & 
                 tau2(icol,ilay,ibnd) * ssa2(icol,ilay,ibnd) * temp_moms(2:nmom1)  ) / tauscat12
            !
            ! Assume all moments of two-stream phase function beyond first moment are 0. 
            !
            p1(1, icol,ilay,igpt) = & 
                (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * p1(1, icol,ilay,igpt) + & 
                 tau2(icol,ilay,ibnd) * ssa2(icol,ilay,ibnd) * g2(   icol,ilay,ibnd)) / tauscat12

            ssa1(icol,ilay,igpt) = tauscat12 / tau12
            tau1(icol,ilay,igpt) = tau12
          end do
        end do
      end do 
    end do
  end subroutine inc_nstream_by_2stream_bybnd
  ! ---------------------------------
  ! increment nstream by nstream
  pure subroutine inc_nstream_by_nstream_bybnd(ncol, nlay, ngpt, nmom1, nmom2, & 
                                               tau1, ssa1, p1,                 & 
                                               tau2, ssa2, p2,                 &
                                               nbnd, gpt_lims)
    integer,                             intent(in   ) :: ncol, nlay, ngpt, nmom1, nmom2, nbnd
    real(wp), dimension(ncol,nlay,ngpt), intent(inout) :: tau1, ssa1
    real(wp), dimension(nmom1, &  
                        ncol,nlay,ngpt), intent(inout) :: p1
    real(wp), dimension(ncol,nlay,nbnd), intent(in   ) :: tau2, ssa2
    real(wp), dimension(nmom2, &  
                        ncol,nlay,nbnd), intent(in   ) :: p2
    integer,  dimension(2,nbnd),         intent(in   ) :: gpt_lims ! Starting and ending gpoint for each band 

    integer  :: icol, ilay, igpt, ibnd, mom_lim
    real(wp) :: tau12, tauscat12

    mom_lim = min(nmom1, nmom2)
    do ibnd = 1, nbnd 
      do igpt = gpt_lims(1, ibnd), gpt_lims(2, ibnd)
        do ilay = 1, nlay
          do icol = 1, ncol
            tau12 = tau1(icol,ilay,igpt) + tau2(icol,ilay,ibnd)
            tauscat12 = & 
               tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) + & 
               tau2(icol,ilay,ibnd) * ssa2(icol,ilay,ibnd)
            !
            ! If op2 has more moments than op1 these are ignored;
            !   if it has fewer moments the higher orders are assumed to be 0 
            ! 
            p1(1:mom_lim, icol,ilay,igpt) = & 
                (tau1(icol,ilay,igpt) * ssa1(icol,ilay,igpt) * p1(1:mom_lim, icol,ilay,igpt) + & 
                 tau2(icol,ilay,ibnd) * ssa2(icol,ilay,ibnd) * p2(1:mom_lim, icol,ilay,ibnd)) / tauscat12
            ssa1(icol,ilay,igpt) = tauscat12 / tau12
            tau1(icol,ilay,igpt) = tau12
          end do
        end do
      end do 
    end do
  end subroutine inc_nstream_by_nstream_bybnd
  ! ---------------------------------

end module mo_optical_props_kernels
